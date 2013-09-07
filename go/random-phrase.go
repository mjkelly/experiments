// random-string generates a configurable random string, for passwords.
package main

import (
	"bufio"
	"crypto/rand"
	"flag"
	"fmt"
	"log"
	"math"
	"math/big"
	"os"
	"regexp"
	"strings"
)

// Flags.
var (
	WordsPerPhrase = flag.Int("words", 5, "Number of words per phrase.")
	NumPhrases     = flag.Int("phrases", 10, "Number of phrases to show.")
	Dictionary     = flag.String("dictionary", "/usr/share/dict/words",
		"Dictionary to use.")
	Quiet = flag.Bool("quiet", false, "Suppress unnecessary output.")
)

// Globals.
var (
	// We only generate phrases from words that match this regexp. Restrictions
	// are: (1) at least 3 chars long, (2) only contains A-Z (any case).
	// The minimum word length restriction is to keep the total passphrase
	// length high, so it's much harder to brute-force the passphrase as a
	// random string than as a passphrase. (That ensures that our entropy
	// calculations, which are based on the string as a passphrase, stay
	// relevant.)
	// TODO(mjkelly): Justify this with some math.
	WordRegexp = regexp.MustCompile(`^[a-zA-Z]{3,}$`)
)

func main() {
	flag.Parse()

	file, err := os.Open(*Dictionary)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	totalWords := 0
	words := make([]string, 0)
	for scanner.Scan() {
		if WordRegexp.MatchString(scanner.Text()) {
			words = append(words, scanner.Text())
		}
		totalWords++
	}

	numWords := len(words)
	numWordsBig := big.NewInt(int64(numWords))
	bitsPerWord := math.Log2(float64(numWords))
	bitsPerPhrase := bitsPerWord * float64(*WordsPerPhrase)
	totalBits := bitsPerPhrase - math.Log2(float64(*NumPhrases))

	if !*Quiet {
		fmt.Printf("%d possible words (of %d in %s).\n", numWords, totalWords, *Dictionary)
		fmt.Printf("%d random words per phrase.\n", *WordsPerPhrase)
		fmt.Printf("∴ %f bits of entropy per word.\n", bitsPerWord)
		fmt.Printf("∴ %f bits of entropy per phrase.\n", bitsPerPhrase)
		fmt.Printf("%d phrases to choose from.\n", *NumPhrases)
		fmt.Printf("∴ %f bits if you pick one phrase from this list.\n", totalBits)
		fmt.Println("---------------------------------------------------")
	}

	for i := 0; i < *NumPhrases; i++ {
		phrase := make([]string, 0, *NumPhrases)
		for j := 0; j < *WordsPerPhrase; j++ {
			randBig, err := rand.Int(rand.Reader, numWordsBig)
			if err != nil {
				log.Fatal(err)
			}
			phrase = append(phrase, words[randBig.Int64()])
		}
		fmt.Println(strings.Join(phrase, " "))
	}
}
