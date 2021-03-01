import json

models = {
    'amd': {
        'models': [
            'RX 5700',
            'RX 5700 XT',
            'RX 6800',
            'RX 6800 XT',
            'RX 6900 XT', ],
        },
    'nvidia': {
        'models': [
            'GTX 1660 Ti',
            'RTX 3060 Ti',
            'RTX 3070',
            'RTX 3080',
            'RTX 3090', ],
        },
    }

for chipset in models:
    with open(f'./{chipset}.txt', 'w') as file:
        json.dump(models[chipset], file)
