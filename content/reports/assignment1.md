# Matrix Multiplication Project Report

**Student Name**: GYILE DENNIS NGMINMAALE  
**Student ID**: LS2425239  
**Submission Date**: Mar 20, 2025


## System Configuration

| Component           | Specification                                                    |
|-------------------- |-------------------------------------------------------------------|
| **CPU Model**       | 12th Gen Intel(R) Core(TM) i7-12700H                             |
| **Memory Size**     | 7.6 GiB RAM, 2.0 GiB Swap                                        |
| **OS Version**      | Linux Priest 5.15.167.4-microsoft-standard-WSL2 (WSL2 on Windows)|
| **Compiler Version**| GCC 13.3.0                                                       |
| **Python Version**  | Python 3.12.3                                                    |


## Implementation Details

### C Language Implementation

- **Source Code**:
```c
#include <stdio.h>

int main() {
    int a[2][2] = {{1, 2}, {3, 4}};
    int b[2][2] = {{5, 6}, {7, 8}};
    int result[2][2];

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            result[i][j] = 0;
            for (int k = 0; k < 2; k++) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    printf("Result matrix:\n");
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            printf("%d ", result[i][j]);
        }
        printf("\n");
    }
    return 0;
}

# Compilation Command
gcc matrix.c -o matrix
# Execution Command
./matrix

### Python Language Implementation
- **Source Code**:
```python
a = [[1, 2], [3, 4]]
b = [[5, 6], [7, 8]]
result = [[0, 0], [0, 0]]

for i in range(2):
    for j in range(2):
        for k in range(2):
            result[i][j] += a[i][k] * b[k][j]

print("Result matrix:")
for row in result:
    print(" ".join(map(str, row)))
# Execution Command
python3 matrix.py


## Algorithm Verification
- Both implementations were tested using 2x2 matrices:
A = [[1, 2],      B = [[5, 6],
     [3, 4]]           [7, 8]]
- Expected result:
[[19, 22],
 [43, 50]]
- Both the C and Python programs output the correct result, confirming the correctness.

## Performance Analysis
-  **Execution Times**:

| Language | Real time           | User   |System  |
|----------|---------------------|--------|--------|
| C        | 0m0.011s            |0m0.001s|0m0.002s|
| Python   | 0m0.106s            |0m0.019s|0m0.000s|

-  **Analysis**:
- C is faster due to compilation and lower-level memory management.
- Python is slower because of its interpreted nature and dynamic typing.
## Conclusion
This project strengthened my skills in:
- Using Unix/Linux command line tools effectively.
- Writing and formatting technical documentation in Markdown.
- Implementing and verifying the same algorithm in both compiled and interpreted languages.

## References
GCC Documentation: https://gcc.gnu.org
Python Docs: https://docs.python.org/3/
WSL Setup Guide: https://learn.microsoft.com/en-us/windows/wsl/

## Appendix
- All tests were done in a WSL2 Ubuntu environment running on Windows 11.
- No external libraries were used.

