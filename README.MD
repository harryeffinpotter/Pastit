# Pastit! (Paste-it)

PRETITIER README COMING SOON - But basically if you know about SPRUNGE.US this is a replacement for that since it has gone MIA, this is the second time its unexplicably gone down in the past ~6 months, and I found myself needing it too often (cant paste into a machine for some reason, weird TTY situiation? EZ win), so I took matters into my own hands.

# REQUIRES ZIPLINE SHAREX BACKEND!
This repo takes the functionality of the zipline repository and makes it a CLI tool, so with these 2 tools combined, you host your own sprunge, basically. That means you can configure it how you like, make it private, limit it to who you want, or make it public and share with the masses!

## How to install:

```git clone https://github.com/harryeffinpotter/pastit```

```cd pastit```

```chmod +x setup.sh```

```./setup.sh```


## Sprunge+ - Like sprunge, but +
### Use pastit to paste files like so

`pastit .zshrc`

`pastit script.py`

`pastit /etc/nginx/nginx.conf`

### Or just capture STDOUT like this-
`ls -la | grep "Feet_pics"| pastit`

`ping lemonparty.org | pastit`

`ip a | pastit`

`echo $YOUR_MUMS_FAVORITE_MAN | sed 's/your dad/me/g' | pastit`






Enjoy! Open to suggestions/ideas! Thanks
