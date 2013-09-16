// markov-sentence-generator generates sentences based on the word frequency
// files output by markov-count.
//
// Depending on the input, they look a little like English sentences, but
// aren't.
package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

var (
	Words = flag.Int("words", 50, "how many words to generate")
)

// Corpus is a full set of word pairs with frequencies.
type Corpus struct {
	F map[string]Freq
}

// Freq is the set of frequencies for a single word and all the words observed
// to follow it.
type Freq struct {
	Word string
	// Next is the list of words following Word. The keys are the words
	// themselves, and the values are the frequencies.
	Next map[string]int
	// NextSum is the sum of all the frequencies in Next, for convenience.
	NextSum int
}

// ReadStats is a collection of statistics about a corpus loaded from disk.
type ReadStats struct {
	// Human readable name for the corpus (e.g., filename).
	Name string
	// The number of pairs loaded.
	Pairs int
	// The total number of words used to generate the corpus.
	Size int
}

// NewCorpus creates a new empty Corpus.
func NewCorpus() *Corpus {
	return &Corpus{
		F: make(map[string]Freq),
	}
}

// AddPair adds words w0 and w1, where w0 preceeds w1, to the *Corpus.
func (c *Corpus) AddPair(w0 string, w1 string, count int) {
	f, found := c.F[w0]
	if !found {
		f.Word = w0
		f.Next = make(map[string]int)
	}
	f.Next[w1] += count
	f.NextSum += count
	// TODO(mjkelly): extra copying here... avoid it.
	c.F[w0] = f
}

// Pick picks a random word from the Corpus, using its word frequencies.
func (c *Corpus) Pick(prev string) string {
	f, found := c.F[prev]
	if !found {
		log.Fatal("word not found in corpus:", prev)
	}

	// This is a relatively dumb algorithm, but it works. It could easily be
	// improved by doing a little more work up front.
	var sortedWords []string
	for w := range f.Next {
		sortedWords = append(sortedWords, w)
	}
	sort.Strings(sortedWords)
	r := rand.Intn(f.NextSum) + 1
	sum := 0
	for _, w := range sortedWords {
		sum += f.Next[w]
		if sum >= r {
			return w
		}
	}
	log.Fatalf("Corpus.Pick failed to find random word! Internal data error. prev=%s, NextSum=%d, f=%d",
		prev, f.NextSum, r)
	return "<ERROR>"
}

// ReadCounts reads a series of word counts from the given file and loads them
// into the receiver. If this function returns a non-nil error, the ReadStats
// struct may be incomplete.
func (corpus *Corpus) ReadCounts(filename string) (error, ReadStats) {
	stats := ReadStats{Name: filename}
	fh, err := os.Open(filename)
	if err != nil {
		return err, stats
	}
	defer fh.Close()

	scanner := bufio.NewScanner(fh)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Split(line, " ")
		if len(parts) != 3 {
			return fmt.Errorf("malformed line: does not have 3 parts: %s", line), stats
		}
		w0, w1 := parts[0], parts[1]
		count, err := strconv.Atoi(parts[2])
		if err != nil {
			return fmt.Errorf("malformed line: cannot parse count part (%s): %s", err, line), stats
		}
		corpus.AddPair(w0, w1, count)
		stats.Pairs++
		stats.Size += count
	}
	return nil, stats
}

func main() {
	flag.Parse()
	if len(flag.Args()) < 1 {
		log.Fatal("not enough arguments: usage: %s <counts_file...>")
	}
	// This is not a cryptographically secure seed, but it's good enough for
	// making funny random sentences.
	rand.Seed(time.Now().UnixNano())

	corpus := NewCorpus()
	for _, arg := range flag.Args() {
		err, stats := corpus.ReadCounts(arg)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Loaded %d pairs (with %d words) from %s.\n", stats.Pairs, stats.Size, stats.Name)
	}

	word := ""
	for i := 0; i < *Words; i++ {
		word = corpus.Pick(word)
		fmt.Printf("%s ", word)
	}
	fmt.Println()
}
