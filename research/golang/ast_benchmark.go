package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// ParseResult contains metrics from parsing a Go file
type ParseResult struct {
	FilePath      string
	ParseTime     time.Duration
	NumFunctions  int
	NumMethods    int
	NumInterfaces int
	NumStructs    int
	Success       bool
	Error         error
}

// FunctionInfo represents extracted function metadata
type FunctionInfo struct {
	Name       string
	Receiver   string // For methods
	Params     []ParamInfo
	Results    []string
	IsExported bool
	LineStart  int
	LineEnd    int
	DocComment string
}

// ParamInfo represents a function parameter
type ParamInfo struct {
	Name string
	Type string
}

// ASTAnalyzer analyzes Go source code
type ASTAnalyzer struct {
	fset    *token.FileSet
	results []ParseResult
}

// NewASTAnalyzer creates a new analyzer
func NewASTAnalyzer() *ASTAnalyzer {
	return &ASTAnalyzer{
		fset:    token.NewFileSet(),
		results: make([]ParseResult, 0),
	}
}

// ParseFile parses a single Go file
func (a *ASTAnalyzer) ParseFile(filePath string) ParseResult {
	start := time.Now()

	f, err := parser.ParseFile(a.fset, filePath, nil, parser.ParseComments)
	if err != nil {
		return ParseResult{
			FilePath: filePath,
			Success:  false,
			Error:    err,
		}
	}

	// Count elements
	var numFunctions, numMethods, numInterfaces, numStructs int

	ast.Inspect(f, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.FuncDecl:
			if x.Recv == nil {
				numFunctions++
			} else {
				numMethods++
			}
		case *ast.InterfaceType:
			numInterfaces++
		case *ast.StructType:
			numStructs++
		}
		return true
	})

	return ParseResult{
		FilePath:      filePath,
		ParseTime:     time.Since(start),
		NumFunctions:  numFunctions,
		NumMethods:    numMethods,
		NumInterfaces: numInterfaces,
		NumStructs:    numStructs,
		Success:       true,
	}
}

// ExtractFunctions extracts all function signatures from a file
func (a *ASTAnalyzer) ExtractFunctions(filePath string) ([]FunctionInfo, error) {
	f, err := parser.ParseFile(a.fset, filePath, nil, parser.ParseComments)
	if err != nil {
		return nil, err
	}

	var functions []FunctionInfo

	ast.Inspect(f, func(n ast.Node) bool {
		fn, ok := n.(*ast.FuncDecl)
		if !ok {
			return true
		}

		info := FunctionInfo{
			Name:       fn.Name.Name,
			IsExported: fn.Name.IsExported(),
			LineStart:  a.fset.Position(fn.Pos()).Line,
			LineEnd:    a.fset.Position(fn.End()).Line,
		}

		// Extract receiver (for methods)
		if fn.Recv != nil && len(fn.Recv.List) > 0 {
			info.Receiver = exprToString(fn.Recv.List[0].Type)
		}

		// Extract parameters
		if fn.Type.Params != nil {
			for _, field := range fn.Type.Params.List {
				typeStr := exprToString(field.Type)
				if len(field.Names) > 0 {
					for _, name := range field.Names {
						info.Params = append(info.Params, ParamInfo{
							Name: name.Name,
							Type: typeStr,
						})
					}
				} else {
					// Unnamed parameter
					info.Params = append(info.Params, ParamInfo{
						Name: "",
						Type: typeStr,
					})
				}
			}
		}

		// Extract return types
		if fn.Type.Results != nil {
			for _, field := range fn.Type.Results.List {
				info.Results = append(info.Results, exprToString(field.Type))
			}
		}

		// Extract doc comment
		if fn.Doc != nil {
			info.DocComment = fn.Doc.Text()
		}

		functions = append(functions, info)
		return true
	})

	return functions, nil
}

// BenchmarkDirectory benchmarks all Go files in a directory
func (a *ASTAnalyzer) BenchmarkDirectory(dir string) error {
	fmt.Println(strings.Repeat("=", 70))
	fmt.Printf("Benchmarking Go files in %s\n", dir)
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println()

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() && filepath.Ext(path) == ".go" {
			result := a.ParseFile(path)
			a.results = append(a.results, result)

			status := "✓"
			if !result.Success {
				status = "✗"
			}

			fmt.Printf("%s %-40s Time: %6.2fms Funcs: %3d Methods: %3d\n",
				status,
				filepath.Base(path),
				float64(result.ParseTime.Microseconds())/1000.0,
				result.NumFunctions,
				result.NumMethods)

			if !result.Success {
				fmt.Printf("  Error: %v\n", result.Error)
			}
		}

		return nil
	})

	return err
}

// PrintSummary prints benchmark statistics
func (a *ASTAnalyzer) PrintSummary() {
	if len(a.results) == 0 {
		fmt.Println("No results to summarize")
		return
	}

	var successful, failed int
	var totalTime time.Duration

	for _, r := range a.results {
		if r.Success {
			successful++
			totalTime += r.ParseTime
		} else {
			failed++
		}
	}

	avgTime := time.Duration(0)
	if successful > 0 {
		avgTime = totalTime / time.Duration(successful)
	}

	fmt.Println()
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println("SUMMARY")
	fmt.Println(strings.Repeat("=", 70))
	fmt.Printf("Total files:        %d\n", len(a.results))
	fmt.Printf("Successful:         %d\n", successful)
	fmt.Printf("Failed:             %d\n", failed)
	fmt.Printf("Total parse time:   %v\n", totalTime)
	fmt.Printf("Average parse time: %.2fms\n", float64(avgTime.Microseconds())/1000.0)
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println()
}

// exprToString converts an ast.Expr to a string representation
func exprToString(expr ast.Expr) string {
	switch t := expr.(type) {
	case *ast.Ident:
		return t.Name
	case *ast.StarExpr:
		return "*" + exprToString(t.X)
	case *ast.SelectorExpr:
		return exprToString(t.X) + "." + t.Sel.Name
	case *ast.ArrayType:
		return "[]" + exprToString(t.Elt)
	case *ast.MapType:
		return "map[" + exprToString(t.Key) + "]" + exprToString(t.Value)
	case *ast.InterfaceType:
		return "interface{}"
	case *ast.StructType:
		return "struct{}"
	default:
		return "unknown"
	}
}

// demoFunctionExtraction demonstrates function extraction
func demoFunctionExtraction() {
	// Create sample Go code
	sampleCode := `package sample

import "fmt"

// Greet greets a person by name
func Greet(name string) string {
	return fmt.Sprintf("Hello, %s!", name)
}

// Calculator is a simple calculator
type Calculator struct {
	value int
}

// Add adds two numbers
func (c *Calculator) Add(a, b int) int {
	return a + b
}

// Multiply multiplies two numbers
func Multiply(x, y int) (int, error) {
	return x * y, nil
}
`

	// Write to temp file
	tmpFile := "sample_code.go"
	if err := os.WriteFile(tmpFile, []byte(sampleCode), 0644); err != nil {
		log.Fatal(err)
	}
	defer os.Remove(tmpFile)

	analyzer := NewASTAnalyzer()
	functions, err := analyzer.ExtractFunctions(tmpFile)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(strings.Repeat("=", 70))
	fmt.Println("FUNCTION EXTRACTION DEMO")
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println()

	for _, fn := range functions {
		fmt.Printf("Function: %s\n", fn.Name)
		if fn.Receiver != "" {
			fmt.Printf("  Receiver: %s\n", fn.Receiver)
		}
		fmt.Printf("  Exported: %v\n", fn.IsExported)
		fmt.Printf("  Parameters: %+v\n", fn.Params)
		fmt.Printf("  Returns: %v\n", fn.Results)
		fmt.Printf("  Lines: %d-%d\n", fn.LineStart, fn.LineEnd)
		if fn.DocComment != "" {
			fmt.Printf("  Doc: %s\n", fn.DocComment)
		}
		fmt.Println()
	}
}

func main() {
	// Demo function extraction
	demoFunctionExtraction()

	// Benchmark current directory
	analyzer := NewASTAnalyzer()
	if err := analyzer.BenchmarkDirectory("."); err != nil {
		log.Fatal(err)
	}
	analyzer.PrintSummary()

	fmt.Println("💡 Next Steps:")
	fmt.Println("1. Download Gin source code and benchmark")
	fmt.Println("2. Test go/types for type inference")
	fmt.Println("3. Test on larger codebases (5000+ LOC)")
	fmt.Println("4. Build call graph using golang.org/x/tools/go/callgraph")
}
