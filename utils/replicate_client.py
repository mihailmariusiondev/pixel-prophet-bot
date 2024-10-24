import replicate

def generate_image(input_data):
    model_version = "mihailmariusiondev/marius-flux:422d4bddab17dadb069e1956009fd55d58ba6c8fd5c8d4a071241b36a7cba3c7"
    output = replicate.run(model_version, input=input_data)
    return output
