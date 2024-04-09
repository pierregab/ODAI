# ==============================================================================
# PROJECT INFORMATION
# ==============================================================================
# Project Title: ODAI
# Version: v1.0.0
# Description: Optical System Design Optimization: Saddle Point Application
# 
# AUTHORS
# ==============================================================================
# Aurélien Argy, Florin Baumann, Jelil Belheine, Pierre-Gabriel Bibal-Sobeaux,
# Benoit Brouillet
# Institution: Télécom Physique Strasbourg, Université de Strasbourg,
# Illkirch-Graffenstaden, France
# 
# LICENSE
# ==============================================================================
# This project is licensed under the GPL 3.0 License. 
# For more details, see the LICENSE file in the project root.
# 
# DATE
# ==============================================================================
# Date of Creation: 04/04/2024
# 
# ==============================================================================
# NOTES
# ==============================================================================
# The code is developed using CodeV version 2022.03 and is intended for use under
# the guidelines of the GPL 3.0 License.
# ==============================================================================



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