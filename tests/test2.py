import os

for file in os.listdir("C:\\Users\\guyst\\Documents\\NetAdmin\\source\\server\\resources\\images\\flags"):
    c = os.path.splitext(os.path.basename(file))[0]
    print(f'<file alias="flag-{c}">images/flags/{c}.png</file>')