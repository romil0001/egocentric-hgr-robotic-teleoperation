# Results Summary

Figures below are reported in the MEng dissertation (April 2024) and poster appendix. Re-run your own trials for new hardware or lighting conditions.

## Gesture recognition accuracy (robust mode)

Per-gesture recognition rates from the dissertation poster / results narrative:

| Gesture | Accuracy |
|---------|----------|
| A | 97.26% |
| B | 96.83% |
| C | 94.56% |
| D | 98.12% |
| E | 95.16% |
| F | 98.09% |
| G | 97.5% |
| H | 98% |
| I | 100% |
| **Mean** | **≈ 97.28%** |

Without the robust confirm gate, mean accuracy was reported near **≈ 55%** under the same evaluation framing—motivating the 5-sample confirmation strategy.

## Latency

| Condition | Reported latency |
|-----------|------------------|
| Without robust confirm | ≈ 0.034 s |
| With robust confirm | higher (on the order of ~0.15 s class; see dissertation plots) |

Trade-off: robust mode improves classification stability at the cost of additional confirmation frames before actuation.

## Qualitative findings

- Basic and complex gestures were successfully mapped to arm motion over Wi-Fi.
- System remained usable under varied lighting when confirm gating was enabled.
- Practical bottlenecks included camera API compatibility on Pi and mechanical stress at servo attachment points (ABS FEA in thesis).

## Reproducibility checklist

1. Match camera resolution (1280×720) and MediaPipe Hands settings.
2. Use identical command vocabulary and `confirm_frames: 5`.
3. Log intended vs predicted labels during a scripted gesture battery.
4. Measure end-to-end latency from classification timestamp to first servo PWM change (logic analyzer / serial markers recommended).

Full discussion: [`dissertation.pdf`](dissertation.pdf), Chapters 4–5.
