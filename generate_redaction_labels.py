import os
from pathlib import Path
import numpy as np
from scipy.signal import stft, medfilt
from scipy.io.wavfile import read


def session_to_segments(input_file, nfft=512, f_cutoff=17, db_red=435, ener_quant=0.1, med_filt_w=31, ener_thresh_ratio=0.95, t_adj_lo=0.02, t_adj_hi=0.08, eps=1e-12):
    #  The regions were filtered with a low-pass filter, so conceptually this
    #   function looks for regions of the recording where the energy above the
    #   cutoff frequency contains sufficiently lower energy than the recording
    #   does in those regions overall.
    #
    #  There is an additional minimum energy requirement for the energy below
    #   the cutoff frequency to avoid false detections on silence regions.
    #  There are additionally some smoothing operations as well.
    #
    #  All of the parameters have been manually tuned based on spot checking
    #   the results of the corpus (both visually, audially, and via the marked
    #   sections of the transcripts. Any remaining errors were manually
    #   corrected outside this function.

    fs, x = read(input_file)
    if len(x.shape) > 1:
        x = x[:, 0]

    f, t, X = stft(x, fs=fs, nfft=nfft)

    red_thresh = np.median(np.sum(np.log(np.abs(X[f_cutoff:, 1000:-1000])+eps), 0)) - db_red
    min_lower_ener = np.quantile(np.sum(np.log(np.abs(X[:f_cutoff, 1000:-1000])+eps), 0), ener_quant)

    pad = (med_filt_w+1)//2

    avg_log_mag = np.pad(np.sum(np.log(np.abs(X[f_cutoff:])+eps), 0), pad, constant_values=red_thresh+db_red)

    regions = (medfilt(avg_log_mag, med_filt_w) < red_thresh).astype(int)[pad:-pad]

    diff = regions[1:]-regions[:-1]
    if regions[0] == 1:
        diff[0] = 1
    if regions[-1] == 1:
        diff[-1] = -1
    inds = np.nonzero(diff)[0]

    out_list = []
    for i in range(0, len(inds), 2):
        lower_ener = np.sum(np.log(np.abs(X[:f_cutoff, inds[i]+1:inds[i+1]+1])+eps), 0)
        if np.sum(lower_ener < min_lower_ener) < ener_thresh_ratio * (inds[i+1]-inds[i]):
            out_list.append([t[inds[i]]+t_adj_lo, t[inds[i+1]]+t_adj_hi])

    return out_list


def main(wav_path="./../WAV/", out_dir="./redactions"):

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for i in range(1, 61):
        session = f"SBC{i:03d}"
        wav_file = Path(wav_path) / f"{session}.wav"
        label_file = out_path / f"{session}.txt"

        if i in [17, 20, 25, 26, 27, 30, 40, 54, 55]:
            # Known to not contain filtered regions (sometimes with false alarms)
            label_file.touch()
            continue

        segs = session_to_segments(wav_file)

        with open(label_file, "w") as outF:
            # Manual additions
            if session == "SBC003":
                segs.append([1400.916, 1400.988])
            elif session == "SBC014":
                segs.append([1417.742, 1418.819])
                segs.append([1419.721, 1421.786])
            elif session == "SBC028":
                segs.append([92.221, 92.318])
            elif session == "SBC032":
                segs.append([45.152, 45.250])
            elif session == "SBC044":
                segs.append([286.390, 286.505])
                segs.append([361.411, 361.518])
            elif session == "SBC060":
                segs.append([739.887, 739.993])

            for seg in segs:
                # Omit known false alarms
                if session == "SBC013" and seg[0] > 95:
                    break
                elif session == "SBC023" and seg[0] > 1462:
                    continue
                elif session == "SBC057":
                    if seg[0] > 874 and seg[0] < 875:
                        continue
                    elif seg[0] > 928 and seg[0] < 929:
                        continue
                    elif seg[0] > 1268 and seg[0] < 1269:
                        continue

                outF.write(f"{seg[0]:0.3f}\t{seg[1]:0.3f}\n")


if __name__ == "__main__":
    main()
