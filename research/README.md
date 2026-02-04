# Research Phase - Phase 1

This directory contains all research materials for evaluating tools and technologies for the Study with Challenge Game platform.

## Directory Structure

```
research/
├── python/          # Python AST and call graph research
├── golang/          # Golang AST and call graph research
├── platforms/       # Competitive analysis of existing platforms
└── reports/         # Consolidated findings and reports
```

## Research Goals

1. **Python Analysis**: Evaluate AST parsing and call graph tools
2. **Golang Analysis**: Evaluate Go's AST tools and call graph generators
3. **Platform Analysis**: Study gamification and UX from competitors
4. **Feasibility**: Validate technical approach for MVP

## Running Benchmarks

### Python Benchmarks
```bash
cd research/python
python ast_benchmarks.py
python callgraph_benchmarks.py
```

### Golang Benchmarks
```bash
cd research/golang
go test -bench=. -benchmem
```

## Key Questions to Answer

1. Which Python call graph library is most accurate?
2. Can we achieve <1s parse time for 1000 LOC?
3. How to handle dynamic Python code?
4. Which Go call graph algorithm balances accuracy and performance?
5. What gamification mechanics work best for code learning?

## Timeline

- Week 1: Python + Golang tool evaluation
- Week 2: Platform analysis + feasibility report

See [implementation_plan.md](../brain/d3da2270-49a5-40f2-856e-1f5ef5ec24f0/implementation_plan.md) for details.
