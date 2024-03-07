## TL;DR
The `scored.uem` file contains algorithmically-detected time marks for the scored (non-filtered) regions of the Santa Barbara Corpus of Spoken American English (SBCSAE), in NIST's UEM format for diarization evaluation.

## Overview
The Santa Barbara Corpus of Spoken American English (SBCSAE) had a low-pass filter applied to regions containing personal information of the participants, while maintaining pitch information ([details here](https://www.linguistics.ucsb.edu/research/santa-barbara-corpus#Recordings)). Though the documentation refers to filter list files containing these regions, they do not appear to be available anywhere that the corpus is hosted. This repo contains an attempt to reconstruct this information via detection of the regions where the filter was applied, so that those regions can be omitted from scoring of technology that might be unfairly negatively impacted by the filtering.

The basic approach is to look for regions of the recordings where the total energy above the cutoff frequency is sufficiently far below the average energy in those regions of the recording overall. An additional step rejects the regions where there is little energy below the cutoff frequency as well, to omit false triggers on silence regions.

The algorithm and parameters were hand-tuned based on spot-checking the outputs (both visually, audially, and via the marked sections of the transcripts). Additional manual edits are included for cases where the algorithm is known to have failed.
