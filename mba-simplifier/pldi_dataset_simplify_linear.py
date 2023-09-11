#!/usr/bin/python3



import re
import sys
import ast
import time
from mba_string_operation import verify_mba_unsat, variable_list
from svector_simplify import SvectorSimplify
from truthtable_search_simplify import PMBASimplify


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

def simplify_lmba(datafile):
    """simplify linear mba expression by the signatrue vector. 
    Args:
        datafile: file storing the original mba expression.
    """
    filewrite = "{source}.simplify.txt".format(source=datafile)

    fw = open(filewrite, "w")
    print("#complex,groundtruth,simplifiedcomplex,simplifiedgroundtruth,z3flag,simtime", file=fw)

    svObj = SvectorSimplify()
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
                start = time.time()
                simExpre1 = svObj.standard_simplify(cmbaExpre, vnumber)
                simExpre2 = svObj.standard_simplify(groundtruth, vnumber)
                elapsed = time.time() - start
                # print("z3 solving...")
                #z3res = verify_mba_unsat(groundtruth, simExpre)
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

def simplify_lmba_single(targetExpr):
    svObj = SvectorSimplify()
    linenum = 0
    line = targetExpr.strip()
    cmbaExpre = line
    vnumber = len(variable_list(cmbaExpre))
    simExpre1 = svObj.standard_simplify(cmbaExpre, vnumber)
    # print("z3 solving...")
    #z3res = verify_mba_unsat(groundtruth, simExpre)
    print(prettify(simExpre1))
    # print(linenum, cmbaExpre, groundtruth, simExpre1, simExpre2, z3res)
    # print("z3 solved: ", z3res)
    # print(cmbaExpre, groundtruth, simExpre1, simExpre2, z3res, elapsed, sep=",", file=fw)
    return None



def main(fileread):
    try:
        simplify_lmba(fileread)
    except:
        print("Error")

    return None



if __name__ == "__main__":
    try:
        fileread = sys.argv[1]
        simplify_lmba_single(fileread)
    except:
        print("error in mba-solver!")



