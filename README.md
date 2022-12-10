<p align="center">
      <img src="http://sun9-87.userapi.com/c627118/v627118100/42db9/7ppi9z9xugg.jpg" width="400">
</p>
<h1 align="center">Word search by QR codes</a>
<h3 align="center">
      <a href="https://docs.google.com/document/d/1HxJ86YWJzMRQRYc6xhSHnRrwHZqNWnkgFet6kvs_mLI/edit#" target="_blank">Case description </a> 
      <a href="https://docs.google.com/document/d/1HxJ86YWJzMRQRYc6xhSHnRrwHZqNWnkgFet6kvs_mLI/edit#" target="_blank">Case solution </a> 
</p>

## About
A project developed for Geoscan Pioneer Mini drone. The project is a case of writing an autonomous flight program using coordinates obtained from **QR codes**. All but one QR codes contain a set of coordinates of three points. On two of them are the letters, that the drone must take a picture of, on the third is the next QR code. The resulting pictures are a combination of the encrypted word. The project also includes a program for recognizing letters from pictures, taken by a drone, and deciphering their combination.

## Documentation
The project includes 4 python script:
1. **letter_searching.py** </p>
The script, which is responsible for the flight of the drone at the given point, the collection of letters and the receipt of the key. The result of the successful execution of the script is the pictures of letters taken at the given points and the key from the Caesar cipher written to a text file. </p>
Main functions:
- *drone_flight()* - drone flight function;
- *read_qr()* - function for reading QR codes.
2. **letter_detection.py** </p>
The script using OCR (Optical Character Recognition), which is responsible for recognizing letters in the pictures taken by the drone. During execution, it writes the recognized letters into the encrypted word, and at the end implements its decryption. </p>
Main functions:
- *letter_writing()* - function for recognizing letters in an image;
- *decoding()* - function to decrypt the received word.
3. **land.py**
Optional script for forced landing of the drone.
4. **stop.py**
Optional script to force disarm the drone.
