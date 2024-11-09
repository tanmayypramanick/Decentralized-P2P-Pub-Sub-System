import subprocess
import time

def start_all_nodes():
    processes = []
    # Start all 8 peer nodes (binary IDs from 000 to 111)
    for i in range(8):
        node_id = format(i, '03b')  # Generate binary IDs (000, 001, ..., 111)
        print(f"Starting node {node_id}...")
        # Run each peer node in a separate process
        process = subprocess.Popen(['python', 'peer_node.py', node_id])
        processes.append(process)
        time.sleep(1)  # Small delay to stagger start times (optional)

    print("All peer nodes are running.")
    return processes

if __name__ == "__main__":
    processes = start_all_nodes()
    try:
        # Keep the main script running so nodes continue to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Terminate all processes on script exit
        for process in processes:
            process.terminate()
        print("All nodes have been stopped.")
