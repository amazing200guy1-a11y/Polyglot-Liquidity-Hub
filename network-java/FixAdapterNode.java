---

### 2. `network-java/FixAdapterNode.java`

```java
/**
 * Polyglot-Liquidity-Hub — FIX Adapter Node (Java 17)
 *
 * Multi-threaded object-pool + buffer manager that serialises
 * transaction streams into institutional-style FIX frames.
 * Designed to keep allocation rate near zero under load.
 */

package liquidity.fix;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.atomic.AtomicLong;

/** Reusable mutable buffer. Returned to the pool after every use. */
final class PooledFixBuffer {
    final StringBuilder sb = new StringBuilder(384);
    final ByteBuffer binary = ByteBuffer.allocate(768);

    void reset() {
        sb.setLength(0);
        binary.clear();
    }
}

/** Fixed-size pool. Blocks on acquire when exhausted (natural back-pressure). */
final class FixBufferPool {
    private final BlockingQueue<PooledFixBuffer> pool;

    FixBufferPool(int capacity) {
        pool = new ArrayBlockingQueue<>(capacity);
        for (int i = 0; i < capacity; i++) {
            pool.offer(new PooledFixBuffer());
        }
    }

    PooledFixBuffer acquire() throws InterruptedException {
        return pool.take();
    }

    void release(PooledFixBuffer buf) {
        buf.reset();
        pool.offer(buf);
    }
}

/**
 * Core FIX adapter node.
 * Thread-safe, GC-aware, ready for high message rates.
 */
public final class FixAdapterNode implements AutoCloseable {

    private final FixBufferPool pool;
    private final AtomicLong framesEncoded = new AtomicLong();
    private final AtomicLong poolAcquisitions = new AtomicLong();

    public FixAdapterNode(int poolSize) {
        if (poolSize < 2) {
            throw new IllegalArgumentException("poolSize must be >= 2");
        }
        this.pool = new FixBufferPool(poolSize);
    }

    /**
     * Encode a NewOrderSingle-style frame.
     * Real production would feed QuickFIX/J or a custom binary encoder.
     */
    public byte[] encodeNewOrder(String symbol, char side, double qty, double price, String clOrdId)
            throws InterruptedException {

        PooledFixBuffer buf = pool.acquire();
        poolAcquisitions.incrementAndGet();

        try {
            // Classic FIX 4.4 tag=value SOH style (simplified for showcase)
            buf.sb
                .append("8=FIX.4.4").append('\u0001')
                .append("35=D").append('\u0001')                 // NewOrderSingle
                .append("11=").append(clOrdId).append('\u0001')
                .append("55=").append(symbol).append('\u0001')
                .append("54=").append(side).append('\u0001')     // 1=Buy 2=Sell
                .append("38=").append(qty).append('\u0001')
                .append("44=").append(price).append('\u0001')
                .append("40=2").append('\u0001')                 // Limit
                .append("59=0").append('\u0001')                 // Day
                .append("10=000").append('\u0001');              // checksum placeholder

            byte[] frame = buf.sb.toString().getBytes(StandardCharsets.US_ASCII);
            framesEncoded.incrementAndGet();
            return frame;
        } finally {
            pool.release(buf);
        }
    }

    public long getFramesEncoded() {
        return framesEncoded.get();
    }

    public long getPoolAcquisitions() {
        return poolAcquisitions.get();
    }

    @Override
    public void close() {
        // Buffers are GC-managed once the pool is unreachable
    }
}
