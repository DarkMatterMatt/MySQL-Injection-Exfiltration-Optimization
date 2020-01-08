# MySQL-Injection-Exfiltration-Optimization

Forked to fix bugs (ported to Python first).

Current (2020-01-08) features of *exploit.py*:

- It works! At least on the test index.php
- Properly implemented the binary tree (which is twice as fast as without one)
- ~4.5 times fewer requests than the "optimised" version in the parent repository

See this blog post for more details on the algorithm.
http://b1twis3.ca/jwt-exfiltration-optimization-with-mysql-injection/
