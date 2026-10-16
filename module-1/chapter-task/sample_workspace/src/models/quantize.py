def quantize(weights, bits=8):
    scale = (2 ** bits - 1) / (max(weights) - min(weights) or 1)
    return [round((w - min(weights)) * scale) for w in weights]
