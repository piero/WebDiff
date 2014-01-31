# WebDiff

## A versatile diff notification system for web pages

### The Problem

Some time ago I wanted to monitor a few web pages, e.g. for news or job announcements. I found some nice browser plugins, but all of them only processed the page text, rather than the underlying code. As a result, they couldn't detect changes in hyperlink targets, unless the link text changed as well.

### My Solution

I wrote *WebDiff* to overcome this problem. It downloads a configurable set of web pages, compares them with the stored previous version, and notifies you by email if any change is detected.

This is a simple implementation for my personal use (it normally runs on one of my *Raspberry Pi*s) but it can be a good starting point for improvements. Have fun!