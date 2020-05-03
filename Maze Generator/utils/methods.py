import random


def get_biased_choices(c_list, bias, relative_weight=5, k=1):
    """Return a sample of the list choosen with a bias

    c_list: Input list
    bias: Bias, -1 favours the first indices, 1 favours the last indices
    relative_weight: This weight is added to the bias when applied to indices
    k: sample size
    """
    c_list_len = len(c_list)
    try:
        if bias == 0:
            random.shuffle(c_list)
            return c_list[0:k]
        return random.choices(c_list, weights=[1 + relative_weight * abs(bias) * (ind if bias >= 0 else c_list_len - 1 - ind) for ind in range(c_list_len)], k=k)
    except IndexError:
        return None
