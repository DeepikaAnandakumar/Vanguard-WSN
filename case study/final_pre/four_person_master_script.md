# Vanguard-WSN: The Team Master Script (20 Minutes)
**Speaker Roles: Aishvarya | Gayatri | Deepika | Anjana**
**Duration: 5 Minutes per Speaker**

---

## **Part 1: Aishvarya (The Hook & Foundation)**
**Time:** 0:00 - 5:00 | **Slides:** 1, 2, 3, 4

### **Slide 1: Title Slide (1:00)**
"Good morning everyone. I am Aishvarya, and alongside my colleagues Gayatri, Deepika, and Anjana, we are thrilled to present **Vanguard-WSN**. Our project isn't just another incremental update to wireless networking. It represents a paradigm shift—a utility-driven framework that achieves a validated **10.21x extension** in sensor network lifetime. We aren't just making networks faster; we are making them sustainable for the future of the massive Internet-of-Things."

### **Slide 2: [1] Problem and Objectives (1:30)**
"Let’s start with the pain point. Most people think sensors die because of 'old age.' That’s a myth. They die because of the **Energy Hole Phenomenon**. Imagine a post office where the people in the back (the edge nodes) have plenty of energy, but the clerks at the front desk (the relay nodes) are overwhelmed by incoming mail. The front desk burns out, and even though 80% of the staff is still healthy, the post office is effectively closed. This is 'Relay Burnout.' Our objective was to move away from the 'stochastic luck' of old protocols like LEACH and build a deterministic system that approaches the theoretical 'God-Line' efficiency."

### **Slide 3: [2] Literature Survey: Comparative Gaps (1:30)**
"But why haven't we solved this yet? If you look at the literature, you see three giants: LEACH, HEED, and PEGASIS. **LEACH** is basic—it picks leaders based on probability. It’s blind. It might pick a half-dead node to lead the whole network. **HEED** uses heavy iterative calculations that often use more battery than they save. **PEGASIS** creates long chains that introduce massive delays. The 'Gap' is clear: the world needs a strategy that is **Utility-Driven**. We need to pick leaders based on their 'fitness'—their energy and their location—rather than just a roll of the dice."

### **Slide 4: [3] Flow Diagram: System Operation (1:00)**
"This brings us to our operational flow. Vanguard operates in a SDN-inspired centralized loop. First, we deploy and initialize. Then, the Base Station conducts a 'Heartbeat'—a global health check. Instead of nodes guessing what to do, the Base Station computes the **Utility Index** for every node, constructs the **Energy-Balanced Path Tree**, and issues specific routing commands back to the field. This ensures that every transmission is part of a globally optimized plan, not a local guess. Now, to explain the technical core of that 'Smart Plan,' I’ll hand it over to Gayatri."

---

## **Part 2: Gayatri (The Implementation & Stability)**
**Time:** 5:00 - 10:00 | **Slides:** 5, 6, 7, 8, 9

### **Slide 5: [4] Proposed Model: The Vanguard Framework (1:15)**
"Thank you, Aishvarya. The 'Secret Sauce' of Vanguard is the **Utility-Driven EBPT Framework**. We don't just look at distance; we look at energy-balance. Our system uses a Directed Acyclic Graph (DAG) construction. This is crucial—it mathematically guarantees that your data never get stuck in a loop. By prioritizing nodes with high residual energy as relays, we effectively 'divert traffic' away from the vulnerable center and distribute the burden across the entire field topology."

### **Slide 6: [5] Implementation: Stack & Radio Physics (1:00)**
"To build this, we stayed away from 'toy simulators.' We used a high-precision Python stack with NumPy and SciPy for vectorized heuristics. We modeled the environment using the **First-Order Radio Energy Model**. We accounted for electronics overhead ($E_{elec}$) and both Free-Space and Multi-Path signal loss. This ensures that our 10x gain is grounded in real IEEE physics, not just simulation shortcuts."

### **Slide 7: [5] Implementation: Core Algorithm (Python) (1:15)**
"Let’s look at the implementation. Here you see our **Utility Index (Ui)** function. It’s an elegant balance: 60% weight on residual energy and 40% on local density. Underneath that is our 'Traffic Diverter'—the `select_parent` logic. Notice the **Gamma factor** ($ \gamma $). This is our 'Fairness Knob.' It allows the code to penalize a node if it is already carrying too many children. This isn't just code; it's a self-correcting mechanical balancing act written in Python."

### **Slide 8: [5] Implementation: Executed Output Receipt (0:45)**
"And here is the proof of execution. This is a snapshot of our `run_experiments` console. You can see the system calculating the **LP Upper Bound** for the specific node placement—in this trial, targeting **3292 rounds**. Our Vanguard EBPT logic hit **2903 rounds** on the first seed. This is what we mean by 'Verified'—the terminal output matches our mathematical claims."

### **Slide 9: [6] Results: 1021% Extension vs. Baselines (0:45)**
"Finally, the 'Million Dollar Slide.' Look at the comparative death curves. LEACH—the red line—collapses early, barely reaching Round 100 before the network fails. Our Vanguard logic—the blue plateau—stays flat and strong all the way to Round 993. That is a **1,021% increase** in uptime. We have effectively kept the network alive 10 times longer than the industry standard baseline. Now, Deepika will take you deeper into *why* these numbers are so high."

---

## **Part 3: Deepika (The Numerical Proof & Logic)**
**Time:** 10:00 - 15:00 | **Slides:** 10, 11, 12, 13, 14

### **Slide 10: [6] Results: Why it Works (Ablation Study) (1:15)**
"Thanks, Gayatri. In research, you have to prove your success isn't an accident. This is our **Ablation Study**. We asked: 'What if we remove the Gamma factor?' or 'What if we use random parent selection?' As you see in Table 3, when you remove our innovations, the performance drops from 92% optimality down to 54%. This proves that the 10x gain is the direct result of our **Utility + EBPT** synergy, not just lucky node placement."

### **Slide 11: [6] Results: Data Harvest and Productivity (1:00)**
"Longevity is useless without productivity. Our Slide 11 shows the **Throughput Gain**. Because our network stays alive 10x longer, we harvest **955% more data packets**. While LEACH shuts down after 12,000 packets, Vanguard delivers over **118,500 messages** to the Base Station. This translates to 10x more environmental data, 10x more security alerts, and 10x more ROI for the network operator."

### **Slide 12: [6] Results: Energy Dissipation Patterns (0:45)**
"Look at these heatmaps. In LEACH, you see deep red 'Energy Holes' near the sink—the system is eating itself from the inside out. In the Vanguard heatmap, the color is cool and balanced. We have effectively 'smeared' the energy depletion across the entire field. This visual is the 'smoking gun' that proves our traffic diverter is working."

### **Slide 13: [6] Results: Comparative Performance Benchmarking (1:00)**
"This matrix is our final data summary. We benchmarked against the **'God-Line'**—the absolute maximum lifetime physically possible for a given topology. While most protocols struggle to hit 40% of the God-Line, Vanguard achieves **92.1%**. This makes it the only protocol in our study that we designate as **'Production Ready.'** It is the closest anyone has come to mathematical perfection in this specific field setup."

### **Slide 14: [7] Challenges and Future Roadmap (1:00)**
"We are honest about the challenges. Centralization at the Base Station does introduce a 'Chatter Tax'—about 5% of energy is spent on health reports. However, we see this as a high-value investment. Our future work involves **Reinforcement Learning**—using AI agents to auto-tune the Gamma factor in real-time as nodes die. We are also moving from simulation to real hardware using Raspberry Pi gateways. To wrap us up and explain the team's journey, I’ll hand it to Anjana."

---

## **Part 4: Anjana (The Team, Legacy & Close)**
**Time:** 15:00 - 20:00 | **Slides:** 15, 16, 17

### **Slide 15: Meet the Team: Case Study Authors (2:00)**
"Thank you, Deepika. This project was a collective effort of specialization. **Deepika** served as our Lead Modeler, owning the complex physics and the $U_i$ derivations. **Gayatri** led the Performance Validation, building the simulation engine we just saw. **Aishvarya** was our Logic Architect, ensuring the EBPT tree remained acyclic and robust. And I served as the Data Specialist, managing the benchmarking against the God-Line and ensuring every claim we made was surgically precise. We didn't just write code; we built a framework where math meets hardware."

### **Slide 16: [8] References (1:00)**
"Our work stands on the shoulders of giants. We have cited the seminal work on LEACH, HEED, and PEGASIS, alongside the IEEE standards for radio energy dissipation. Every graph you saw today is reproducible using the parameters defined in these foundational papers, ensuring that Vanguard remains an open, verifiable contribution to the WSN research community."

### **Slide 17: Conclusion (2:00)**
"In conclusion, Vanguard-WSN is the 'Smart Battery' for the Internet of Things. By closing **92.1% of the God-Line gap** and extending stability by **1,021%**, we have proven that deterministic control beats probabilistic luck every time. We are solving the most expensive problem in remote sensing: the early death of healthy nodes. Thank you for your time, and we are now open for any technical questions you may have."
