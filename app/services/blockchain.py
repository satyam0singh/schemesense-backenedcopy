import os
import json
import base64
from datetime import datetime
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# For Testnet, we can use AlgoNode's public node
ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "") # No token needed for AlgoNode public node

def get_algod_client():
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

class BlockchainService:
    def __init__(self, sender_mnemonic: str = None):
        self.client = get_algod_client()
        if sender_mnemonic:
            self.mnemonic = sender_mnemonic
            self.private_key = mnemonic.to_private_key(sender_mnemonic)
            self.address = account.address_from_private_key(self.private_key)
        else:
            # Generate a temporary account for illustration (needs funding)
            self.private_key, self.address = account.generate_account()
            self.mnemonic = mnemonic.from_private_key(self.private_key)
    
    def store_hash(self, doc_hash: str):
        """
        Store a document hash as a transaction note on Algorand.
        """
        params = self.client.suggested_params()
        
        # We store the hash in the transaction note (limit 1KB)
        note = json.dumps({"type": "doc_verification", "hash": doc_hash}).encode()
        
        # Sending a 0-ALGO transaction to ourselves with the note
        txn = transaction.PaymentTxn(
            sender=self.address,
            sp=params,
            receiver=self.address,
            amt=0,
            note=note
        )
        
        # Sign the transaction
        signed_txn = txn.sign(self.private_key)
        
        # Send the transaction
        txid = self.client.send_transaction(signed_txn)
        
        # Wait for confirmation
        wait_for_confirmation(self.client, txid)
        
        return {
            "tx_id": txid,
            "hash_preview": f"{doc_hash[:10]}...",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "explorer_url": f"https://testnet.algoscan.app/tx/{txid}"
        }

    def verify_hash(self, txid: str, doc_hash: str):
        """
        Verify that a specific transaction on Algorand contains the given document hash.
        """
        try:
            tx_info = self.client.pending_transaction_info(txid)
        except Exception:
            # If not pending, it might be in an older block
            # For simplicity, we assume we need to check the explorer or an indexer
            # In a real app, use an Indexer.
            return False, "Transaction not found or too old for current node cache."

        # Decode the note
        try:
            note_base64 = tx_info.get("note")
            if not note_base64:
                return False, "No blockchain record found for this transaction."
            
            note_bytes = base64.b64decode(note_base64)
            note_data = json.loads(note_bytes.decode())
            
            stored_hash = note_data.get("hash")
            hash_preview = f"{stored_hash[:10]}..."
            
            if stored_hash == doc_hash:
                return True, {
                    "verified": True,
                    "message": "Document is authentic and not tampered.",
                    "hash_preview": hash_preview,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            else:
                return False, {
                    "verified": False,
                    "message": "Document has been modified after upload.",
                    "hash_preview": f"Stored: {hash_preview} | Current: {doc_hash[:10]}..."
                }
        except Exception as e:
            return False, f"Error decoding on-chain data: {str(e)}"

def wait_for_confirmation(client, txid):
    """
    Wait until the transaction is confirmed or rejected.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo
