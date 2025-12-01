import time
c = '='
print()
for i in range(101):
    print(f'\r{i*c}{i}%', end='', flush=True)
    time.sleep(0.05)
print()
