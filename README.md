![Oakestra](https://github.com/oakestra/oakestra/raw/develop/res/oakestra-white.png)

[![](https://img.shields.io/badge/USENIX%20ATC%20'23-paper-limegreen)](https://www.oakestra.io/pubs/Oakestra-ATC2023.pdf)
[![](https://img.shields.io/badge/wiki-website-blue)](https://www.oakestra.io/docs/)
[![](https://img.shields.io/badge/Discord-%235865F2.svg?&logo=discord&logoColor=white)](https://discord.gg/7F8EhYCJDf)


<img width="40%" src="https://raw.githubusercontent.com/oakestra/oakestra.github.io/69dc5022f80ec4e9b90254ce69b12f05aa5f9d0d/pubs/badges/badges.png" align="right" />

# Oakestra USENIX ATC 2023 Artifacts 
## Network Repository

This repository contains the artifacts for the paper:

### Oakestra: A Lightweight Hierarchical Orchestration Framework for Edge Computing

> **Abstract:** Edge computing seeks to enable applications with strict latency requirements by utilizing resources deployed in diverse, dynamic, and possibly constrained environments closer to the users. Existing state-of-the-art orchestration frameworks(e.g. Kubernetes) perform poorly at the edge since they were designed for reliable, low latency, high bandwidth cloud environments. We present Oakestra, a hierarchical, lightweight, flexible, and scalable orchestration framework for edge computing. Through its novel federated three-tier resource management, delegated task scheduling, and semantic overlay networking, Oakestra can flexibly consolidate multiple infrastructure providers and support applications over dynamic variations at the edge. Our comprehensive evaluation against the state-of-the-art demonstrates the significant benefits of Oakestra as it achieves an approximately tenfold reduction in resource usage through reduced management overhead and 10% application performance improvement due to lightweight operation over constrained hardware.

[Oakestra](https://oakestra.io) is an open-source project. Most of the code used for this paper is upstream, or is in the process of being upstreamed.

```
@inproceedings {Bartolomeo2023,
author = {Bartolomeo, Giovanni and Yosofie, Mehdi and Bäurle, Simon and Haluszczynski, Oliver and Mohan, Nitinder and Ott, Jörg},
title = {{Oakestra}: A Lightweight Hierarchical Orchestration Framework for Edge Computing},
booktitle = {2023 USENIX Annual Technical Conference (USENIX ATC 23)},
year = {2023},
address = {Boston, MA},
url = {https://www.usenix.org/conference/atc23/presentation/bartolomeo},
publisher = {USENIX Association},
month = jul,
}
```

## Artifact Structure

<img src="https://github.com/oakestra/USENIX-ATC23-Oakestra-Artifacts/assets/5736850/73baf8e0-621a-4e16-844c-a480e0040912" width="60%" />

There are a total of three artifact repositories for reproducing the experiments and results in the paper. 

1. [Orchetrator repository](https://github.com/oakestra/USENIX-ATC23-Oakestra-Artifacts/tree/main/Experiments): The  repository contains the Root & Cluster orchestrators   folders, as well as the Node Engine source code for the worker node.

2. [**This**] [Network repository](https://github.com/oakestra/USENIX-ATC23-Oakestra-net-Artifacts): This repository contains the  Root, Cluster, and Worker network components.

3. [Experiments repository](https://github.com/oakestra/USENIX-ATC23-Oakestra-Artifacts/tree/main/Experiments): This repository includes the setup instructions to create your first Oakestra infrastructure and a set of scripts to automate the results collection procedure and reproducing our results.

4. [_Optional_] [Dashboard](https://github.com/oakestra/dashboard): The repository contains a front-end application that can be used to graphically interact with the platform. Its optional but gives a nice web-based GUI to Oakestra

### Q. I want to recreate the experiments in the paper. What should I do?

A. We have created a detailed `README` and `getting-started` guide that provides step-by-step instructions which you can find [here](https://github.com/oakestra/USENIX-ATC23-Oakestra-Artifacts/blob/main/Experiments/README.pdf).

> The rest of the repository will detail how to set up the Oakestra orchestrators. You can just follow these steps or take a look at our README file for instructions.

### Q. I just want to try out Oakestra. Should I continue with this repo?

A. This repository is recreating our USENIX ATC artifacts and is, therefore, out-of-sync of the main Oakestra development. Please see the `main` [Oakestra](https://github.com/oakestra/oakestra) for the latest features.

---

## What is inside this repository?

This is the networking component that enables interactions between the microservices deployed in Oakestra. 
The networking component resembles the multi-layer architecture of Oakestra with the following components:

- Root service manager: register the cluster service manager and generates the subnetwork for each worker and cluster belonging to the infrastructure.
- Cluster service manager: this is the direct interface towards the nodes. This resolves the addresses required by each node. 
- NetManager: It's deployed on each node. It's responsible for the maintenance of a dynamic overlay network connecting the nodes.

This networking component creates a semantic addressing space where the IP addresses not only represent the final destination for a packet
but also enforces a balancing policy.

### Prerequisites

- Linux OS with
  - iptable
  - ip util
- port 10010   

### Installation

Download the NetManager package, install it using `./install.sh <architecture>` and then execute it using `sudo NetManager`

### Semantic addressing (ServiceIPs)

A semantic address enforces a balancing policy towards all the instances of a service. 

- RR_IP (Currently implemented): IP address pointing every time to a random instance of a service. 
- Closest_IP (Under implementation): IP address pointing to the closest instance of a service.

Example: Given a service A with 2 instances A.a and A.b
- A has 2 ServiceIPs, a RR_IP and a Closest_IP. 
- A.a has an instance IP representing uniquely this instance.
- A.b has another instance IP representing uniquely this instance.
- If an instance of a service B uses the RR_IP of A, the traffic is balanced request after request toward A.a or A.b

The implementation happens at level 4, therefore as of now all the protocols absed on top of TCP and UDP are supported.

### Subnetworks

An overlay that spans seamlessly across the platform is only possible if each node has an internal sub-network that can be used to allocate an address for each newly deployed service. When a new node is attached to Oakestra, a new subnetwork from the original addressing space is generated. All the services belonging to that node will have private namespace addresses belonging to that subnetwork.
As of now the network 10.16.0.0/12 represents the entire Oakestra platform. From this base address each cluster contains subnetworks with a netmask of 26 bits that are assigned to the nodes. Each worker can then assign namespace ip addresses using the last 6 bits of the address. A namespace ip is yeat another address assigned to each instance only within the node boundaries. The address 10.30.0.0/16 is reserved to the ServiceIPs.
This network cut enables up to ≈ 15.360 worker nodes. Each worker can instantiate ≈ 62 containers, considering the address reserved internally for the networking components. 

### Packet proxying

The component that decides which is the recipient worker node for each packet is the ProxyTUN. This component is implemented as an L4 proxy which analyzes the incoming traffic, changes the source and destination address, and forwards it to the overlay network.
A packet approaching the proxy has a namespace IP as the source address and an IP belonging to the subnetwork of the Service and Instance IPs as a destination. 
The L4 packet also has a couple of source and destination ports used to maintain a connection and contact the correct application on both sides. The proxy’s job is to substitute the source and destination addresses according to the routing policy expressed by the destination address. 
The proxy converts the namespace address of the packet, belonging to the local network of the node, with the InstanceIP of that service’s instance.
This conversion enables the receiver to route the response back to the service instance deployed inside the sender’s node.
If the original destination address is an InstanceIP, the conversion is straightforward using the information available in the proxy’s cache. When the original destination address is a ServiceIP, the following four steps are executed:

- Fetch the routing policy
- Fetch the service instances
- Choose one instance  using the logic associated with the routing policy 
- Replace the ServiceIP with the namespace address of the resulting instance.

After the correct translation of source and destination addresses, the packet is encapsulated and sent to the tunnel only if the destination belongs to another node, or it is just sent back down to the bridge if the destination is in the same node.
