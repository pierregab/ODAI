############## Console output functions ##############


def print_evolution_header(starting_depth, target_depth):
    ascii_art = """
                 __            __ 
                /  |          /  |
  ______    ____$$ |  ______  $$/ 
 /      \  /    $$ | /      \ /  |
/$$$$$$  |/$$$$$$$ | $$$$$$  |$$ |
$$ |  $$ |$$ |  $$ | /    $$ |$$ |
$$ \__$$ |$$ \__$$ |/$$$$$$$ |$$ |
$$    $$/ $$    $$ |$$    $$ |$$ |
 $$$$$$/   $$$$$$$/  $$$$$$$/ $$/                                                         
                                  
    """
    print(ascii_art)
    print("=" * 80)
    print(f"Starting System Evolution from Depth {starting_depth} to {target_depth}")
    print("=" * 80)


def print_subheader(title):
    print("\n" + "-" * 80)
    print(f"{title}")
    print("-" * 80)

def print_header(title):
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)

def print_decorative_header():
    print("\n" + "=" * 80)
    print("""             ___ ____ ____ ____    ____ ___ ____ ___ ____ 
              |  |__/ |___ |___    [__   |  |__|  |  |___ 
              |  |  \ |___ |___    ___]  |  |  |  |  |___                                     
            """)
    print("=" * 80 + "\n")

def print_blank_line():
    print("\n"*3)