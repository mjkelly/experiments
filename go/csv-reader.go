// csv-reader is a quick-and-dirty app for querying the contents of CSV files.
//
// It's useful mainly if the files are long (more than a few MB), and have many
// (>20) columns.

package main

import (
	"bufio"
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
)

// parseLine reformats a list of values from the CSV file as a map from header
// name to value.
func parseLine(headers []string, values []string) (map[string]string, error) {
	kv := make(map[string]string)
	if len(values) != len(headers) {
		return nil, fmt.Errorf("Expected %d records, got %d.",
			len(headers), len(values))
	}
	for i, header := range headers {
		kv[header] = values[i]
	}
	return kv, nil
}

// matches determines whether the subset of 'data' whose keys overlap with
// 'query' has the same value as the values in 'query'.
// E.g., query = {a:1, b:2}, data = {a:1, b:2, c:3} --> true
//       query = {a:2, b:2}, data = {a:1, b:2, c:3} --> false
func matches(query map[string]string, data map[string]string) bool {
	for key, value := range query {
		dataValue, ok := data[key]
		if !ok {
			return false
		}
		if value != dataValue {
			return false
		}
	}
	return true
}

// parseQuery parses the 'query' arguments, which are a list of key=value
// strings.
func parseQuery(query []string) (map[string]string, error) {
	queryMap := make(map[string]string)
	for _, kv := range query {
		split := strings.SplitN(kv, "=", 2)
		if len(split) != 2 {
			return nil, fmt.Errorf("each query argument must be of form \"key=value\"")
		}
		queryMap[split[0]] = split[1]
	}
	return queryMap, nil
}

// filterFields filters a map 'values' by a list of keys, specified in
// 'columns'. The resulting map contains only those keys (the values are
// unchanged). If 'columns' is empty, filterFields returns 'values' verbatim.
func filterFields(columns []string, values map[string]string) map[string]string {
	if len(columns) == 0 {
		return values
	}
	result := make(map[string]string)
	for _, col := range columns {
		val, ok := values[col]
		if ok {
			result[col] = val
		}
	}
	return result
}

func usage() {
	log.Fatalf("Usage: %s [--output=Col1,Col2] <data_file> [<query=val> ...]",
		os.Args[0])
}

func main() {
	outputFlag := flag.String("output", "", "Columns to output.")
	flag.Parse()

	var outputColumns []string
	if *outputFlag != "" {
		outputColumns = strings.Split(*outputFlag, ",")
		fmt.Printf("Outputting columns: %q\n", outputColumns)
	}

	query := make(map[string]string)
	var err error
	argv := flag.Args()
	if len(argv) < 1 {
		log.Print("<data_file> is required")
		usage()
	}
	if len(argv) > 1 {
		query, err = parseQuery(argv[1:])
		if err != nil {
			log.Fatal(err)
		}
	}

	fh, err := os.Open(argv[0])
	if err != nil {
		log.Fatal(err)
	}
	defer fh.Close()
	c := csv.NewReader(bufio.NewReader(fh))

	headers, err := c.Read()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Columns: %q\n", headers)

	matchCount := 0
	for {
		records, err := c.Read()
		if err != nil {
			if err == io.EOF {
				return
			} else {
				log.Fatal(err)
			}
		}
		kv, err := parseLine(headers, records)
		if err != nil {
			log.Fatal(err)
		}
		if matches(query, kv) {
			matchCount += 1
			fmt.Printf("Match %d: %q\n", matchCount, filterFields(outputColumns, kv))
		}
	}
}
