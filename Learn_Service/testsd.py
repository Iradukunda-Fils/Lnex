#impost sys
#print(sys.version, sys.platform)

# class Node:
#    def __init__(self, data):
#        self.data = data
#        self.next = None

# class Tree:
#   def __init__(self):
#      self.head = None
#      self.tail = None
#   def append(self, data):
#      if not self.head:
#         self.head = Node(data)
#         self.tail = self.head

#      self.head.next = Node(data)
#      self.tail = self.head.next

#   def display(self):
#     current = self.head
#     while current:
#        print(current.data, end=" -> ")
#        current = current.next

# ll = Tree()
# ll.append([820,232,232,232,3232,42])
# ll.append([423,23,2,4,34,23,323,42])    
# ll.append([42334,23,323,232,23,342])

# ll.display()






# print("hell, ubuntu", end=",,,,")


deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg] https://apt.postgresql.org/pub/repos/apt/ noble-pgdg main
