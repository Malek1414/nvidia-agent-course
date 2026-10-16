#!/usr/bin/env bash
# Re-run jobs that failed overnight
python -m src.app --retry-failed
