#!/usr/bin/python3



import re
import sys
import ast
import time
from mba_string_operation import verify_mba_unsat, variable_list, expression_2_term
from svector_simplify import SvectorSimplify
from truthtable_search_simplify import PMBASimplify


def simplify_linear_combination(mbaExpre):
    """
    """
    #basisVec2 = ["x", "y", "(x|y)", "~(x&~x)"]
    basisVec2 = ["(x&y)", "(~x&y)", "(x&~y)", "(~x&~y)"]
    basisVec4 = ["x", "y", "z", "t", "(x&y)",  "(x&z)", "(x&t)", "(y&z)", "(y&t)","(z&t)", "(x&y&z)", "(x&y&t)", "(x&z&t)", "(y&z&t)", "(x&y&z&t)", "~(x&~x)"]
    #basisVec4 = ["(x&y&z&t)", "(~x&y&t&z)", "(x&~y&z&t)", "(x&y&~z&t)", "(x&y&z&~t)",  "(~x&~y&z&t)", "(x&~y&~z&t)", "(x&y&~z&~t)", "(~x&y&~z&t)","(~x&y&z&~t)", "(x&~y&z&~t)", "(x&~y&~z&~t)", "(~x&y&~z&~t)", "(~x&~y&z&~t)", "(~x&~y&~z&t)", "(~x&~y&~z&~t)"]
    termList = expression_2_term(mbaExpre)
    xytermList = []
    nxytermList = []
    for term in termList:
        if len(variable_list(term)) == 2:
            xytermList.append(term)
        else:
            nxytermList.append(term)
    xyExpre = "".join(xytermList)
    nxyExpre = "".join(nxytermList)
    psObj = PMBASimplify(2, basisVec2)
    simxyExpre = psObj.simplify(xyExpre)
    psObj = PMBASimplify(4, basisVec4)
    simnxyExpre = psObj.simplify(nxyExpre)
    if simnxyExpre[0] == "-" or simnxyExpre[0] == "+":
        simExpre = simxyExpre + simnxyExpre
    else:
        simExpre = simxyExpre + "+" + simnxyExpre

    return simExpre

def prettify(formula):
    def traverse(node):
        if isinstance(node, ast.Module):
            return traverse(node.body[0])
        if isinstance(node, ast.Expr):
            return traverse(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return "0u"+str(node.value)
        if isinstance(node, ast.BinOp):
            return "(" + traverse(node.left) + " " + traverse(node.op) + " " + traverse(node.right) + ")"
        if isinstance(node, ast.UnaryOp):
            return "(" + traverse(node.op) + " " + traverse(node.operand) + ")"
        if isinstance(node, ast.Add):
            return "bvadd" if not prettify else "+"
        if isinstance(node, ast.Sub):
            return "bvsub" if not prettify else "-"
        if isinstance(node, ast.Mult):
            return "bvmul" if not prettify else "*"
        if isinstance(node, ast.Div):
            return "bvudiv" if not prettify else "/"
        if isinstance(node, ast.Mod):
            return "bvurem" if not prettify else "%"
        if isinstance(node, ast.LShift):
            return "bvshl" if not prettify else "<<"
        if isinstance(node, ast.RShift):
            return "bvlshr" if not prettify else ">>"
        if isinstance(node, ast.BitOr):
            return "bvor" if not prettify else "|"
        if isinstance(node, ast.BitXor):
            return "bvxor" if not prettify else "^"
        if isinstance(node, ast.BitAnd):
            return "bvand" if not prettify else "&"
        if isinstance(node, ast.USub):
            return "bvneg" if not prettify else "-"
        if isinstance(node, ast.Invert):
            return "bvnot" if not prettify else "~"
    return traverse(ast.parse(formula))

def simplify_pmba(datafile):
    """simplify poly mba expression by the signatrue vector. 
    Args:
        datafile: file storing the original mba expression.
    """
    filewrite = "{source}.simplify.txt".format(source=datafile)

    fw = open(filewrite, "w")
    print("#complex,groundtruth,simplifiedcomplex,simplifiedgroundtruth,z3flag,simtime", file=fw)

    linenum = 0
    with open(datafile, "rt") as fr:
        for line in fr:
            if "#" not in line:
                linenum += 1
                line = line.strip()
                itemList = re.split(",", line)
                cmbaExpre = itemList[0]
                groundtruth = itemList[1]
                vnumber = len(variable_list(cmbaExpre))
                if vnumber == 1:
                    #basisVec = ["x","~(x&~x)"]
                    basisVec = ["x","~x"]
                elif vnumber == 2:
                    basisVec = ["x", "y", "(x|y)", "~(x&~x)"]
                    #basisVec = ["(x&y)", "(~x&y)", "(x&~y)", "(~x&~y)"]
                elif vnumber == 3:
                    basisVec = ["x", "y", "z", "(x&y)",  "(y&z)", "(x&z)", "(x&y&z)", "~(x&~x)"]
                    #basisVec = ["(x&y&z)", "(~x&y&z)", "(x&~y&z)", "(x&y&~z)",  "(~x&~y&z)", "(~x&y&~z)", "(x&~y&~z)", "(~x&~y&~z)"]
                elif vnumber == 4:
                    #basisVec = ["x", "y", "z", "t", "(x&y)",  "(x&z)", "(x&t)", "(y&z)", "(y&t)","(z&t)", "(x&y&z)", "(x&y&t)", "(x&z&t)", "(y&z&t)", "(x&y&z&t)", "~(x&~x)"]
                    basisVec = ["(x&y&z&t)", "(~x&y&t&z)", "(x&~y&z&t)", "(x&y&~z&t)", "(x&y&z&~t)",  "(~x&~y&z&t)", "(x&~y&~z&t)", "(x&y&~z&~t)", "(~x&y&~z&t)","(~x&y&z&~t)", "(x&~y&z&~t)", "(x&~y&~z&~t)", "(~x&y&~z&~t)", "(~x&~y&z&~t)", "(~x&~y&~z&t)", "(~x&~y&~z&~t)"]
                if vnumber == 4:
                    start = time.time()
                    simExpre1 = simplify_linear_combination(cmbaExpre)
                    simExpre2 = simplify_linear_combination(groundtruth)
                    elapsed = time.time() - start
                    # print("z3 solving...")
                    z3res = verify_mba_unsat(simExpre1, simExpre2, 2)
                    # print(linenum, cmbaExpre, groundtruth, simExpre1, simExpre2, z3res)
                    # print("z3 solved: ", z3res)
                    if z3res:
                        print(prettify(simExpre1))
                    else:
                        print("error in mba-solver!")
                    # print(cmbaExpre, groundtruth, simExpre1, simExpre2, z3res, elapsed, sep=",", file=fw)
                    continue
                psObj = PMBASimplify(vnumber, basisVec)
                start = time.time()
                simExpre1 = psObj.simplify(cmbaExpre)
                simExpre2 = psObj.simplify(groundtruth)
                elapsed = time.time() - start
                # print("z3 solving...")
                z3res = verify_mba_unsat(simExpre1, simExpre2, 2)
                if z3res:
                    print(prettify(simExpre1))
                else:
                    print("error in mba-solver!")
                # print(linenum, cmbaExpre, groundtruth, simExpre1, simExpre2, z3res)
                # print("z3 solved: ", z3res)
                # print(cmbaExpre, groundtruth, simExpre1, simExpre2, z3res, elapsed, sep=",", file=fw)

    fw.close()
    return None



def simplify_pmba_single(targetExpr):
    line = targetExpr.strip()
    cmbaExpre = line
    vnumber = len(variable_list(cmbaExpre))
    if vnumber == 1:
        #basisVec = ["x","~(x&~x)"]
        basisVec = ["x","~x"]
    elif vnumber == 2:
        basisVec = ["x", "y", "(x|y)", "~(x&~x)"]
        #basisVec = ["(x&y)", "(~x&y)", "(x&~y)", "(~x&~y)"]
    elif vnumber == 3:
        basisVec = ["x", "y", "z", "(x&y)",  "(y&z)", "(x&z)", "(x&y&z)", "~(x&~x)"]
        #basisVec = ["(x&y&z)", "(~x&y&z)", "(x&~y&z)", "(x&y&~z)",  "(~x&~y&z)", "(~x&y&~z)", "(x&~y&~z)", "(~x&~y&~z)"]
    elif vnumber == 4:
        #basisVec = ["x", "y", "z", "t", "(x&y)",  "(x&z)", "(x&t)", "(y&z)", "(y&t)","(z&t)", "(x&y&z)", "(x&y&t)", "(x&z&t)", "(y&z&t)", "(x&y&z&t)", "~(x&~x)"]
        basisVec = ["(x&y&z&t)", "(~x&y&t&z)", "(x&~y&z&t)", "(x&y&~z&t)", "(x&y&z&~t)",  "(~x&~y&z&t)", "(x&~y&~z&t)", "(x&y&~z&~t)", "(~x&y&~z&t)","(~x&y&z&~t)", "(x&~y&z&~t)", "(x&~y&~z&~t)", "(~x&y&~z&~t)", "(~x&~y&z&~t)", "(~x&~y&~z&t)", "(~x&~y&~z&~t)"]
    if vnumber == 4:
        start = time.time()
        simExpre1 = simplify_linear_combination(cmbaExpre)
        # print("z3 solving...")
        # print(linenum, cmbaExpre, groundtruth, simExpre1, simExpre2, z3res)
        # print("z3 solved: ", z3res)
        print(prettify(simExpre1))
        # print(cmbaExpre, groundtruth, simExpre1, simExpre2, z3res, elapsed, sep=",", file=fw)
    psObj = PMBASimplify(vnumber, basisVec)
    simExpre1 = psObj.simplify(cmbaExpre)
    # print("z3 solving...")
    print(prettify(simExpre1))
    # print(linenum, cmbaExpre, groundtruth, simExpre1, simExpre2, z3res)
    # print("z3 solved: ", z3res)
    # print(cmbaExpre, groundtruth, simExpre1, simExpre2, z3res, elapsed, sep=",", file=fw)
    return None


def main(fileread):
    simplify_pmba(fileread)

    return None



if __name__ == "__main__":
    try:
        fileread = sys.argv[1]
        simplify_pmba_single(fileread)
    except:
        print("error in mba-solver!")



