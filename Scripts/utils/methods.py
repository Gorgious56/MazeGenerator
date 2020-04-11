import random


def get_biased_choice(c_list, bias, relative_weight=5, k=1):
    """Return a sample of the list choosen with a bias

    c_list: Input list
    bias: Bias, -1 favours the first indices, 1 favours the last indices
    relative_weight: This weight is added to the bias when applied to indices
    k: sample size
    """
    bias = max(0.00001, bias)
    c_list_len = len(c_list)
    try:
        if bias == 0:
            random.shuffle(c_list)
            return c_list[0: k + 1] if k > 1 else c_list[0]
        ret = random.choices(c_list, weights=[1 + relative_weight * abs(bias) * (ind if bias >= 0 else c_list_len - 1 - ind) for ind in range(c_list_len)], k=k)
        return ret[0] if k == 1 else ret
    except IndexError:
        return None
