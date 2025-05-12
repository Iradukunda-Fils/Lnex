# from pathlib import Path

# d = "files_dirs"

# print("data is here")
# print(Path('file', 'data', d).resolve())


# li = ['data', "43", "hello", "3.14"]

# def gen():
#     for i in li:
#         yield i

# print(map( li,i for i in li))

# print(i for i in li if i)



# class Node:
#     def __init__(self, value):
#         self.data = value
#         self.next = None
        
# class LinkedList:
#     def __init__(self):
#         self.head = None
#         self.last = None
        
#     def append(self, data):
#         new_node = Node(data)
#         if not self.head:
#             self.head = new_node
#             self.last = self.head
#             return
#         self.last.next = new_node
#         self.last = new_node
        
        
#     def display(self):
#         current = self.head
#         while current:
#             print(current.data, end=" -> ")
#             current = current.next
#         print("None")
        
# ll = LinkedList()
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])
# ll.append(["data", "help"])

# ll.display()

# class Node:
#     def __init__(self):
#         self.data = None
#         self.left = None
#         self.right = None
        
# class Tree:
#     def __init__(self):
#         self.root = None
#         self.last = None
#         self.count = 0
    
#     def append(self):
#         new_node = Node()
#         if not self.root:
#             self.root = new_node
#             self.last = self.root
#             self.count += 1
#             return
#         self.last.right = new_node
#         self.last = new_node
#         self.count += 1
    
#     def display(self):
#         current = self.root
#         while current:
#             print(current.data, end=" -> ")
#             current = current.right
            

from collections import defaultdict
# import pkg_resources

# Raw input: lines of packages (some with duplicates)
raw_packages = """
asgiref==3.8.1
certifi==2025.1.31
charset-normalizer==3.4.1
colorama==0.4.6
Django==5.1.7
django-appconf==1.1.0
django-countries==7.6.1
django-environ==0.12.0
django-extensions==3.2.3
django-rosetta==0.10.1
django-statici18n==2.6.0
idna==3.10
iniconfig==2.1.0
lxml==5.3.2
packaging==24.2
pillow==11.1.0
pluggy==1.5.0
polib==1.2.0
psycopg2-binary==2.9.10
PyPDF2==3.0.1
pytest==8.3.5
pytest-django==4.11.1
python-docx==1.1.2
python-magic==0.4.27
python-pptx==1.0.2
requests==2.32.3
sqlparse==0.5.3
typing_extensions==4.13.0
tzdata==2025.2
urllib3==2.3.0
XlsxWriter==3.2.2
asgiref==3.8.1
audioread==3.0.1
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==3.4.1
colorama==0.4.6
contourpy==1.3.2
cycler==0.12.1
decorator==5.2.1
Django==5.1.7
django-appconf==1.1.0
django-countries==7.6.1
django-environ==0.12.0
django-extensions==3.2.3
django-rosetta==0.10.1
django-statici18n==2.6.0
ffmpeg-python==0.2.0
fonttools==4.57.0
future==1.0.0
idna==3.10
iniconfig==2.1.0
joblib==1.4.2
kiwisolver==1.4.8
lazy_loader==0.4
librosa==0.11.0
llvmlite==0.44.0
lxml==5.3.2
matplotlib==3.10.1
msgpack==1.1.0
numba==0.61.2
numpy==2.2.5
packaging==24.2
pillow==11.1.0
platformdirs==4.3.7
pluggy==1.5.0
polib==1.2.0
pooch==1.8.2
psycopg2-binary==2.9.10
pycparser==2.22
pyparsing==3.2.3
PyPDF2==3.0.1
pytest==8.3.5
pytest-django==4.11.1
python-dateutil==2.9.0.post0
python-docx==1.1.2
python-gettext==5.0
python-magic==0.4.27
python-pptx==1.0.2
requests==2.32.3
scikit-learn==1.6.1
scipy==1.15.2
six==1.17.0
soundfile==0.13.1
soxr==0.5.0.post1
sqlparse==0.5.3
threadpoolctl==3.6.0
typing_extensions==4.13.0
tzdata==2025.2
urllib3==2.3.0
XlsxWriter==3.2.2
"""

# Step 1: Parse and deduplicate, keeping highest version seen
pkg_versions = defaultdict(str)
for line in raw_packages.strip().splitlines():
    if "==" in line:
        name, version = line.strip().split("==")
        if name.lower() not in pkg_versions or pkg_versions[name.lower()] < version:
            pkg_versions[name.lower()] = version

# Step 2: Format sorted output (by name)
deduped_sorted_packages = sorted((name, version) for name, version in pkg_versions.items())

deduped_sorted_packages[:10]  # Show first few for review


