from attackcti import attack_client

# Initialize ATT&CK client
client = attack_client()

# Get all techniques in ATT&CK
techniques = client.get_techniques()

print(f"Total ATT&CK Techniques: {len(techniques)}")
