from   itertools import permutations, product
import itertools

def model_masks():

    MASKS_5 = ['10111','11011','11101']
    MASKS_4 = ['1011' , '1101']
    MASKS_3 = ['101', ]

    masks_5 = []
    masks_4 = []
    masks_3 = []

    for n in [0,1,2,3]:
        masks_5.extend(permutations(MASKS_5, n))

    for n in [0,1,2]:
        masks_4.extend(permutations(MASKS_4, n))

    for n in [1,]:
        masks_3.extend(permutations(MASKS_3, n))

    masks = product(masks_5, masks_4, masks_3)
    for m in masks:
        yield tuple(itertools.chain.from_iterable(m))


def sorted_model_masks():

    l = [(len(mask_tup), tuple(mask_tup)) for mask_tup in model_masks()]
    l.sort()
    l2 = [mask_tup for _ , mask_tup in l]
    for n_mask, mask_tup in enumerate(l2):
        # print n_mask, mask_tup
        yield mask_tup

if __name__ == '__main__':

    for i, smm in enumerate(sorted_model_masks()):
        print i, smm

