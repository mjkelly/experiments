// markov-counts takes an input file and generates a list of word frequencies
// based on which words follow which (Markov chains).
package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"
	"unicode"
)

// NonAlphanum returns true for runes that are not alphanumeric or
// sentence-terminating punctuation marks.
//
// Keeping the punctuation marks is a hack so that we can generate things that
// look like full sentences. ("foo." tends to be followed by a capitalized
// word, etc.)
func NonAlphanum(r rune) bool {
	return !(unicode.IsLetter(r) || unicode.IsNumber(r) || r == '.' || r == '?' || r == '!')
}

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Not enough args")
	}
	fh, err := os.Open(os.Args[1])
	if err != nil {
		log.Fatal(err)
	}
	defer fh.Close()

	scanner := bufio.NewScanner(fh)
	scanner.Split(bufio.ScanWords)

	// counts is a map of maps. The first-level key is the preceding word, the
	// second-level key is the following word, and the value is the number of
	// times the preceding word occurs before the following word. The empty
	// string is used to indicate "no word".
	//
	// For example, the following sentence:
	//   "the dog chases the small dog"
	// Would produce:
	// counts := {
	//   "": {
	//     "the": 1
	//   }
	//   "the": {
	//     "dog": 1,
	//     "small": 1,
	//	 },
	//   "dog": {
	//     "chases": 1,
	//	 },
	//   "chases": {
	//     "the": 1,
	//	 },
	//   "small": {
	//     "dog": 1,
	//	 },
	// }
	counts := make(map[string]map[string]int)
	prev := ""
	for scanner.Scan() {
		cur := scanner.Text()
		// Clean up words a little to make things simpler.
		cur = strings.TrimFunc(cur, NonAlphanum)
		if len(cur) == 0 {
			continue
		}
		_, found := counts[prev]
		if !found {
			counts[prev] = make(map[string]int)
		}
		counts[prev][cur]++
		prev = cur
	}

	// The final output format of the map is simply:
	//   key1 key2 count
	// Words cannot contain spaces, so this is safe. 'count' is an integer
	// count in base 10. One count per line.
	for prevWord, nextMap := range counts {
		for nextWord, count := range nextMap {
			fmt.Println(prevWord, nextWord, count)
		}
	}
}
