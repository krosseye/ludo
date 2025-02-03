#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################

import random
import string


def generate_id():
    num = random.getrandbits(32)
    chars = string.digits + string.ascii_lowercase
    if num == 0:
        return chars[0]
    result = []
    while num:
        result.append(chars[num % 36])
        num //= 36
    return "".join(reversed(result))


if __name__ == "__main__":
    for i in range(10):
        print("Base-36 ID:", generate_id())
