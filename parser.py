# import sys


# class FileParser:
#     def __init__(self, name_file: str):
#         self.name_file = name_file

#     def fetch_infos(self) -> list[str]:
#         settings: list[str] = []
#         try:
#             with open(self.name_file, 'r') as file:
#                 for line_num, line in enumerate(file, 1):
#                     cleaned_line = line.strip()
#                     if not cleaned_line or cleaned_line.startswith("#"):
#                         continue
#                     if ":" not in cleaned_line:
#                         print(f"[Error] Line {line_num} The format is "
#                               "'key:value [optional=detail]'")
#                         sys.exit(0)

#                     settings.append(cleaned_line)
#         except OSError:
#             print(f"[Error] Cannot read file named: {self.name_file}.")
#             sys.exit(0)
#         if not settings:
#             print("[Error] Empty datas setting.")
#             sys.exit(0)
#         return settings
