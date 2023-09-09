

def formatMv(mv,index):
    print(f"######## {index} #######")
    print(mv.date)
    print(mv.product.name)
    print("type : ", mv.mvt_type)
    print("old : ",mv.old_quantity)
    print("new : ",mv.new_quantity)
    