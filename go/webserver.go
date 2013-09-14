// This is a very simple webserver that serves a given direcotry with HTTP
// digest authentication.
//
// I use it to serve email attachments that I want to access removelty, so the
// serving directory is ~/attachments.
package main

import (
	auth "github.com/abbot/go-http-auth"
	"log"
	"net/http"
	"os"
	"path"
)

func Secret(user, realm string) string {
	// HA1 is md5(username + ":" + realm + ":" password)
	switch user {
	case "duplex":
		// duplex:attachments:agreements
		return "c24813d49c5d20bad97ebad923b68bcd"
	default:
		return ""
	}
}

const (
	// Auth controls whether to use authorization. It isn't a command-line
	// option, but it's here for debugging.
	Auth = true
)

func main() {
	dir := path.Join(os.Getenv("HOME"), "attachments")
	port := "8080"
	if len(os.Args) > 1 {
		dir = os.Args[1]
	}
	if len(os.Args) > 2 {
		port = os.Args[2]
	}

	h := http.FileServer(http.Dir(dir))
	if Auth {
		authenticator := auth.NewDigestAuthenticator("attachments", Secret)
		// This is a little awkward: http.FileServer is a Handler (the object),
		// but authenticator.Wrap only takes a HandlerFunc. So, we make
		// conversion function.
		f := func(w http.ResponseWriter, r *auth.AuthenticatedRequest) {
			h.ServeHTTP(w, &r.Request)
		}
		http.HandleFunc("/", authenticator.Wrap(f))
	} else {
		http.Handle("/", h)
	}
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
