// random-string generates a configurable random string, for passwords.
package main

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"math"
	"math/rand"
	"time"
)

// Flags.
var (
	PasswordLength = flag.Int("length", 16, "Length of password to generate.")
	LowerAlphaNum  = flag.Bool("loweralphanum", false,
		"Only generate passwords with lowercase alphanumeric characters. "+
			"Mutually exclusive with --alphanum.")
	AlphaNum = flag.Bool("alphanum", false,
		"Only generate passwords with alphanumeric characters. "+
			"Mutually exclusive with --loweralphanum.")
	Quiet = flag.Bool("quiet", false, "Suppress unnecessary output.")
)

// Possible characters to be used in passwords.
var (
	LowerAlphaNumChars = []byte{'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
		'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
		'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
	UpperAlphaChars = []byte{'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
		'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
		'Z'}
	SymbolChars = []byte{'~', '!', '@', '#', '%', '^', '&', '*', '(', ')', '-',
		'_', '=', '+', '[', ']', '{', '}', '|', ';', ':', '<', '>', ',', '.',
		'/', '?'}
)

func main() {
	flag.Parse()
	if *LowerAlphaNum && *AlphaNum {
		log.Fatal("--loweralphanum and --alphanum are mutually exclusive!")
	}

	chars := []byte(LowerAlphaNumChars)
	if !*LowerAlphaNum {
		chars = append(chars, UpperAlphaChars...)
	}
	if !*AlphaNum && !*LowerAlphaNum {
		chars = append(chars, SymbolChars...)
	}
	numChars := len(chars)
	bitsPerChar := math.Log2(float64(numChars))
	totalBits := bitsPerChar * float64(*PasswordLength)

	// TODO(mjkelly): I've read that the math/rand package is extremely
	// predictable, and seeding it with the current time only gives a few bytes
	// of entropy anyway. Figure out a better source of randomness.
	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	fmt.Println("*** WARNING! ***")
	fmt.Println("Seeding random values with time.Now().UnixNano(), which may " +
		"not be good enough. This program is currenly a curiosity only. Don't " +
		"use it for passwords you care about.")
	fmt.Println("*** WARNING! ***\n")

	if !*Quiet {
		fmt.Printf("%d characters long.\n", *PasswordLength)
		fmt.Printf("Choosing from %d characters. %2.3f bits of entropy per character.\n",
			numChars, bitsPerChar)
		fmt.Printf("%2.3f total bits of entropy.\n\n", totalBits)
		fmt.Println("Password:")
	}

	var passBuffer bytes.Buffer
	for i := 0; i < *PasswordLength; i++ {
		randChar := chars[r.Intn(numChars)]
		passBuffer.WriteByte(randChar)
	}

	fmt.Println(passBuffer.String())
}
