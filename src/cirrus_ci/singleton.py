#!/usr/bin/env python3

def singleton(cls):
    instances = {}

    def get(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
        
    return get
