// Polyglot-Liquidity-Hub — Go Channel Multiplexer
//
// Ultra-fast data router built on native goroutines and buffered channels.
// Zero shared mutable state between workers; all coordination via channels.

package main

import (
	"context"
	"fmt"
	"log"
	"sync"
	"sync/atomic"
	"time"
)

// TrafficVector represents a single market-data or order event.
type TrafficVector struct {
	Symbol    string
	Side      string
	Quantity  float64
	Price     float64
	Timestamp time.Time
	Source    string
}

// Endpoint is a downstream consumer identified by name.
type Endpoint struct {
	Name string
	Ch   chan<- TrafficVector
}

// Router is a lock-free (from the caller's perspective) fan-out multiplexer.
type Router struct {
	ingress   chan TrafficVector
	endpoints []Endpoint
	routed    atomic.Uint64
	dropped   atomic.Uint64
	wg        sync.WaitGroup
}

// NewRouter creates a router with a bounded ingress buffer.
func NewRouter(buffer int) *Router {
	return &Router{
		ingress: make(chan TrafficVector, buffer),
	}
}

// RegisterEndpoint adds a downstream consumer.
// The supplied channel should be buffered by the caller.
func (r *Router) RegisterEndpoint(name string, ch chan<- TrafficVector) {
	r.endpoints = append(r.endpoints, Endpoint{Name: name, Ch: ch})
}

// Start launches the single dispatcher goroutine.
func (r *Router) Start(ctx context.Context) {
	r.wg.Add(1)
	go r.dispatch(ctx)
}

// Submit pushes a vector into the ingress channel (non-blocking try).
func (r *Router) Submit(v TrafficVector) bool {
	select {
	case r.ingress <- v:
		return true
	default:
		r.dropped.Add(1)
		return false
	}
}

func (r *Router) dispatch(ctx context.Context) {
	defer r.wg.Done()
	for {
		select {
		case <-ctx.Done():
			return
		case v, ok := <-r.ingress:
			if !ok {
				return
			}
			r.fanOut(v)
		}
	}
}

// fanOut delivers a copy of the vector to every registered endpoint.
// Uses non-blocking sends so a slow consumer cannot stall the router.
func (r *Router) fanOut(v TrafficVector) {
	for _, ep := range r.endpoints {
		select {
		case ep.Ch <- v:
			r.routed.Add(1)
		default:
			// Endpoint is saturated — drop for this consumer only
			r.dropped.Add(1)
		}
	}
}

// Stats returns simple counters for observability.
func (r *Router) Stats() (routed, dropped uint64) {
	return r.routed.Load(), r.dropped.Load()
}

// Wait blocks until the dispatcher exits.
func (r *Router) Wait() {
	r.wg.Wait()
}

// ---------------------------------------------------------------------------
// Demo main (optional)
// ---------------------------------------------------------------------------
func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	router := NewRouter(1024)

	// Two sample endpoints
	marketData := make(chan TrafficVector, 256)
	orderFlow := make(chan TrafficVector, 256)
	router.RegisterEndpoint("market-data", marketData)
	router.RegisterEndpoint("order-flow", orderFlow)

	router.Start(ctx)

	// Simulate ingress
	go func() {
		for i := 0; i < 1000; i++ {
			router.Submit(TrafficVector{
				Symbol:    "EURUSD",
				Side:      "B",
				Quantity:  1.0,
				Price:     1.0850 + float64(i%10)*0.0001,
				Timestamp: time.Now().UTC(),
				Source:    "simulator",
			})
		}
		close(router.ingress)
	}()

	// Drain one endpoint for demo
	go func() {
		for range marketData {
			// consume
		}
	}()

	router.Wait()
	routed, dropped := router.Stats()
	log.Printf("routed=%d dropped=%d", routed, dropped)
	fmt.Println("Go router finished")
}
