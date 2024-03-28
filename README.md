# Optical System Design Optimization: Saddle Point Application
<img
  src="logo_final.png"
  alt="Alt text"
  title="Optional title"
  style="display: inline-block; margin: 0 auto; width: 15%;">


![ODAI Logo](logo_final.png)

The Optical System Design Optimization project employs the saddle point method in an application that interfaces with CodeV software, offering a novel yet experimental approach to optical system design. While the application presents a new way to explore optical system configurations, it is important to note that outcomes can be highly sensitive to initial parameters and the specific system under consideration.

## Project Overview

This application provides an optimization workflow that integrates the saddle point method with the powerful optical design capabilities of CodeV. It's designed for those looking to explore alternative approaches in optical system design, particularly in the realm of wide-angle eyepieces.

### Key Features

- **Saddle Point Method**: Implements the saddle point method for optical system design, providing a fresh perspective on finding local minima in design space.
- **User Interface**: Features a GUI that facilitates interaction with the application, making it more accessible for users unfamiliar with programming.
- **CodeV Compatibility**: Developed to work in conjunction with CodeV, taking advantage of its optimization capabilities.
- **Data Analysis Tools**: Includes Python scripts for data analysis, such as tree creation and merit function evaluation, adding a layer of flexibility to the design process.

## Repository Structure

- **main_classes**: The main directory with essential Python scripts, including `main.py` as the entry point for the application.
- **Python_file_for_SPIE_paper**: Contains files related to the development of a paper for the SPIE conference and is not necessary for the operation of the application itself.

## Getting Started

To use this application in your optical design endeavors, follow these instructions:

1. **Setup Your Environment**:
   Make sure you have Python and CodeV installed as the application depends on both.

2. **Clone the Repository**:
   Retrieve the project onto your local machine:
   ```sh
   git clone https://github.com/pierregab/ODAI.git
   ```

3. **Install Python Dependencies**:
   Install the required libraries with pip:
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   Start the main script to initiate the design process. The GUI will provide step-by-step guidance.

### Alternative: Pre-built Application

If you prefer not to deal with environment setup or code modification, we offer a pre-built version of the application. Download it from the provided repository link and follow the included instructions for use.

## Contributing

Your input is welcome, particularly if you have ideas for improving the application, whether by tweaking the optimization algorithms, enhancing the GUI, or extending the app's functionality.

## License

This project is made available under the 3PL 3.0 License. Consult the [LICENSE](LICENSE) file for more details.

## Acknowledgements

We acknowledge and thank the contributors from Télécom Physique Strasbourg and ICube Laboratory, Université de Strasbourg, for their support and input into this project.
