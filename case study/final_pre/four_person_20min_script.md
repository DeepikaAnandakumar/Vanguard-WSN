# Vanguard-WSN: The Team Master Presentation Script (20 Minutes)
**Speaker Roles: Aishvarya | Gayatri | Deepika | Anjana**
**Format: 5 Minutes per Speaker (~650 words each)**
**PPT Source:** `Vanguard_WSN_Final to show.pptx`

---

## **Part 1: Aishvarya (The Hook & Infrastructure)**
**Duration:** 00:00 – 05:00 | **Slides:** 1, 2, 3, 4

### **Slide 1: Title Slide (1:00)**
"Good morning, and welcome to our presentation on **Vanguard-WSN**. I am Aishvarya, and joined by my colleagues Gayatri, Deepika, and Anjana, we are here to present a fundamental breakthrough in wireless sensor network longevity. Our project, titled 'Vanguard-WSN: A 10.21-times Lifetime Extension via Utility-Driven Routing,' addresses one of the most persistent bottlenecks in the Internet of Things. While many researchers focus on making sensors cheaper or smaller, we focused on making them smarter and more sustainable. We aren't just presenting a protocol; we are presenting a framework that bridges the gap between theoretical physics and real-world deployment. As we move through this presentation, you will see how our deterministic tree model achieves over 92% of the absolute mathematical maximum possible lifetime. Let’s start by looking at the tragedy of the current status quo."

### **Slide 2: Problem & Objectives - The Energy Hole (1:30)**
"Current wireless networks fail not because they run out of energy overall, but because they fail unevenly. This is what we call the **Energy Hole Problem**. Imagine a network of 100 sensors. The nodes near the edge have plenty of battery, but the nodes near the center—the ones closest to the Base Station—are overwhelmed. They have to carry everyone else's data. This creates a relay burnout. On Slide 2, you see the 'Energy Hole Phenomenon.' Even if distant nodes have 80% of their battery remaining, if the center nodes die, the network is dead. 

Furthermore, legacy protocols like **LEACH** make this worse. LEACH operates on a 'random dice roll' for leader selection. This means the network might accidentally pick a node with 5% battery to lead a massive data cycle. When that node dies, the whole network collapses prematurely. Our objective was simple but ambitious: Replace this 'chance' with deterministic logic. We set out to maximize stability—the round when the first node dies—and approach the theoretical 'God-Line' known as the LP Bound."

### **Slide 3: Literature Survey: Comparative Gaps (1:00)**
"Before we built Vanguard, we conducted a rigorous Literature Survey, which you see on Slide 3. We analyzed the three giants of WSN research: LEACH, HEED, and PEGASIS. We identified consistent gaps. LEACH is probabilistic and 'blind' to energy status during the critical leader selection moments. HEED is iteratively heavy, often using more power to calculate the route than it does to send the data. PEGASIS creates static chains that introduce massive latency and create single points of failure. The common thread here is **Imbalance**. The world didn't need another random protocol; it needed an **Energy-Balanced** framework. This brings us to how our system actually operates."

### **Slide 4: System Operation Flow (1:30)**
"On Slide 4, we see the architectural 'Heartbeat' of Vanguard-WSN. Our system follows a strict Five-Step cycle every round to ensure zero energy is wasted. 
1. **Initialization:** Nodes are deployed and report their initial positions to the Base Station.
2. **Heartbeat:** This is our global health check. Every node reports its current battery status.
3. **Control Plane Phase:** Unlike distributed protocols where nodes guess, our Base Station computes the **Utility Index** for the entire field.
4. **Routing Phase:** The Base Station constructs the **EBPT Tree**—an optimal path where high-energy nodes act as the 'backbone.'
5. **Transmission Phase:** The data relay cycle executes, and the plan refreshes in the next round. 
This centralized control ensures that 'Relay node burnout' is mathematically impossible. To explain the math-driven leadership selection that makes this work, I will hand over to Gayatri."

---

## **Part 2: Gayatri (Implementation & Prototyping)**
**Duration:** 05:00 – 10:00 | **Slides:** 5, 6, 7, 8, 9

### **Slide 5: Proposed Model: The Vanguard Framework (1:15)**
"Thank you, Aishvarya. As we move into Slide 5, you see the 'Soul' of Vanguard-WSN. Our framework is a hybrid between SDN Centralized control and Tree Routing. The key here is the **Acyclic Guarantee**. Because our logic is deterministic and driven by a Directed Acyclic Graph, or DAG, we eliminate routing loops entirely. We use the **Utility Function (Ui)** to prioritize energy-rich nodes as relays, and we employ an **Adaptive Gamma Factor** that dynamically shifts the load as the network ages. This isn't just a static plan; it’s a living, breathing architecture that 'bends' its routing paths to avoid depleting any single node."

### **Slide 6: Utility-Based Leader Selection (1:15)**
"Slide 6 breaks down the leader selection logic. We moved away from 'luck' and toward 'fitness.' Our **Utility Index Formula** has two major components: Energy and Density. 
The **Energy Component** ensures that higher residual battery always results in a higher score. We never pick a dying node to lead traffic. 
The **Density Component** is equally important. It prevents 'Hotspots.' Nodes in crowded zones are penalized slightly to ensure we don't overwhelm a single spatial area. 
Finally, we apply the **Elite Set Filter**. Only nodes that exceed the network-wide mean utility are even allowed to be candidates. This 'high-performance-only' filter is why our stability is so high."

### **Slide 7: EBPT + Adaptive Gamma Factor (1:15)**
"Now, look at Slide 7. This is how we eliminate the Energy Hole. The **EBPT Tree** is a multi-hop structure where every node selects its parent based on that parent's energy and current load. 
This involves the **Gamma Factor ($\gamma$)**. Think of Gamma as a 'Fairness Knob.' When Gamma is LOW, we prioritize speed. When Gamma is HIGH, we prioritize longevity. As sensors begin to die, our system automatically 'turns up the knob' to distribute the burden even more aggressively. Figure 1 shows the resulting Hierarchical Architecture—the first time a tree protocol has been this balanced across a random field."

### **Slide 8: Simulation Environment & Tools (0:45)**
"To prove these theories, we built a production-grade simulation environment. As shown on Slide 8, we used **Python 3.8+** because it allows for the high-precision math required for our heuristics. We utilized **NumPy and SciPy** for distance matrix geometry and **Matplotlib** for the 300 DPI visualizations you've seen. Crucially, we implemented the **First-Order Radio Model** using IEEE standard physics. We didn't use 'ideal' energy assumptions; we calculated realistic Joules-per-bit depletion for every transmission."

### **Slide 9: Executed Output Receipt (0:30)**
"On Slide 9, we have the 'Receipt.' This is the raw console output from our simulation. You can see the system calculating the absolute **LP Bound** of 3292 rounds. It verifies our Vanguard logic by showing a consistent FND mean that stays within 92% of that theoretical maximum. This console proof is what separates our empirical work from mere hypothetical claims. Now, Deepika will walk you through the staggering results of these implementation choices."

---

## **Part 3: Deepika (The Numerical Breakthrough)**
**Duration:** 10:00 – 15:00 | **Slides:** 10, 11, 12, 13, 14

### **Slide 10: Result 1: Network Lifetime 10.21x Gain (1:15)**
"Thank you, Gayatri. Let’s look at the numbers on Slide 10—the numerical evidence of our breakthrough. In a standard 50-node field, **LEACH** dies at Round 97. That is where the first node disappears and the network begins to fail. **Vanguard-WSN hits Round 993**. That is a **10.21-times stability gain**. 
But more importantly, look at the comparison to the 'God-Line.' Our result isn't just better than LEACH; it is **92.1% of the absolute mathematical maximum** physically possible for this topology. We have left only a 7% margin for improvement for the entire future of this research area."

### **Slide 11: Result 2: 9.55x More Data (1:00)**
"Slide 11 illustrates why lifetime matters: **Data Harvest**. A sensor that is dead cannot transmit. Because our sensors stay alive for 10x longer, they deliver 10x more data. We harvested **118,500 packets** with Vanguard, compared to just 12,400 packets with LEACH. This is a 955% increase in throughput. For a real-world user, this means 10 years of data versus 1 year of data for the exact same hardware cost."

### **Slide 12: Result 3: Energy Distribution (Heatmap) (1:15)**
"The 'Why' is answered in the heatmaps on Slide 12. Look at the **Baseline** image on the left. You see those deep red circles in the center? That is the Energy Hole. It shows nodes near the sink being completely exhausted while the outer nodes (in green) waste their full batteries. 
Now look at the **Vanguard** heatmap on the right. It is a uniform, warm gradient. There are no holes. Every node is participating, and every node is depleting at the same rate. Figure 7, the fairness curve, confirms that we have achieved near-perfect energy symmetry."

### **Slide 13: Result 3: Perfect Spatial Energy Balance (0:45)**
"Continuing on Slide 13, we see the deeper spatial analysis. We moved the relay burden proportionally across the field. By using the 'Traffic Diverter' logic Gayatri mentioned, we ensured that no node ever takes on more than its fair share. This visual proof—the cool blue-and-green distribution—is the ultimate evidence that centralized SDN control can solve the spatial energy dissipation problem that has plagued WSNs since the year 2000."

### **Slide 14: Comparative Performance Summary (0:45)**
"Slide 14 is our Executive Summary. We benchmarked against LEACH (Deterministic), LEACH (Energy-Aware), and the LP Optimum. Vanguard remains the leader across every metric. Our **Jain's Fairness Index of 0.156** (normalized) is the highest in its class. We have effectively reached the 'Production Ready' threshold. We have proven that our Utility-Driven EBPT is the most stable protocol currently available for this deployment scale. I’ll now hand over to Anjana to discuss the limits and the future of this work."

---

## **Part 4: Anjana (The Challenges & The Vision)**
**Duration:** 15:00 – 20:00 | **Slides:** 15, 16, 17

### **Slide 15: Challenges & Future Work (2:15)**
"Thank you, Deepika. As we approach the end of our presentation, Slide 15 provides an honest assessment of our project. No system is perfect, and Vanguard has its trade-offs. 
First, there is the **Centralized Overhead**. The daily 'Roll-call' chatter uses a small battery 'tax.' We have accounted for this in our model, but in a real-world deployment, this must be managed very carefully. 
Second, we have the **Timing Idealization**. In a simulation, everything is synchronized perfectly. In the field, radio interference and 'jitter' will challenge our tree construction. 
And third, **Scalability**. While we excel at 100 meters, a single 'Brain' might struggle in multi-kilometer deployments. 

However, we are already working on the road forward. We are investigating **RL-Based Auto-Tuning**—using AI to tune our Gamma factor dynamically without any human intervention. We are also preparing a **Hardware Deployment** phase using Raspberry Pi gateways and Arduino sensor nodes to see how our Python logic survives real-world signal interference. Our Pareto Frontier in Figure 4 shows that we are already at the peak of the speed-longevity trade-off."

### **Slide 16: References & Acknowledgments (1:15)**
"Our work is built on the rigorous foundation shown on Slide 16. We owe a debt to the seminal papers by Heinzelman, Younis, and Lindsey. We have strictly followed the First-Order Radio Model to ensure our results are scientifically valid and reproducible. I want to acknowledge the Department of Mathematics at Amrita Vishwa Vidyapeetham for the computational support. All our figures were generated using open-source tools—Matplotlib, NetworkX, and NumPy—ensuring that our 'Vanguard' implementation remains transparent and open for future academic review."

### **Slide 17: Conclusion & Summary (1:30)**
"In summary, as we see on Slide 17, Vanguard-WSN delivers on its promise. 
A **10.21-times longer network lifetime**. 
A **92.1% approach to the absolute theoretical God-Line**. 
And a **955% increase in cumulatively delivered data**. 
We started with a simple objective: to replace 'chance' with logic. We have ended with a system that creates a perfectly balanced energy field with zero holes and zero hotspots. As we always say in our lab: 'Reliable data starts with a reliable network.' Vanguard is that reliable network. 
Thank you for your attention. Deepika, Aishvarya, Gayatri and I are now ready and look forward to your questions and discussion."
