import base64

def decode_base64(encoded_str):
    try:
        # A Base64 kódolt string visszaalakítása eredeti bájtokra,
        # majd dekódolás UTF-8 formátumban
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return "Hiba a dekódolás során: " + str(e)

if __name__ == "__main__":
    encoded_input = input("Add meg a Base64 kódolt jelszót: ")
    decoded = decode_base64(encoded_input)
    print("A dekódolt jelszó:", decoded)