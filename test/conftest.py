def pytest_assertrepr_compare(op, left, right):
    if left.__class__.__name__ == "ModuleSpy" or \
            right.__class__.__name__ == "ModuleSpy" and \
            op == "==":
        str_list = ["Module is not equal"]
        for l, r in zip(left, right):
            if isinstance(l, list):
                for sub_l, sub_r in zip(l, r):
                    if sub_l == sub_r:
                        s = "    == '%s', '%s'" % (sub_l[:25], sub_r[:25])
                    else:
                        s = "    != '%s', '%s'" % (sub_l[:25], sub_r[:25])
                    str_list.append(s)
            else:
                if l == r:
                    s = "== '%s', '%s'" % (l[:30], r[:30])
                else:
                    s = "!= '%s', '%s'" % (l[:30], r[:30])
                str_list.append(s)
        return str_list
