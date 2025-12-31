from eml4806.graphics.style import Style


# Usage examples
if __name__ == "__main__":
    # All these store as RGB tuples
    style1 = Style(color='red')
    print(style1)  # (1.0, 0.0, 0.0)
    
    style2 = Style(color='#FF5733')
    print(style2)  # (1.0, 0.34117647058823, 0.2)
    
    style3 = Style(color=(0.5, 0.5, 0.5))
    print(style3)  # (0.5, 0.5, 0.5)
    
    # RGB method just returns stored value
    print(style1.rgb())   # (1.0, 0.0, 0.0)
    print(style1.rgba())  # (1.0, 0.0, 0.0, 1.0)
    
    # Update with validation
    style1.set(color='blue', alpha=0.5)
    print(style1.to_matplotlib())  # (0.0, 0.0, 1.0)