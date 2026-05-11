"""
Script to generate IEEE-formatted LaTeX document from Vanguard WSN paper
Preserves all original content while applying IEEE conference template formatting
"""

import re

def escape_latex(text):
    """Escape special LaTeX characters"""
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(chars.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: chars[match.group()], text)

def create_latex_doc():
    latex_header = r"""\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts
% The preceding line is only needed to identify funding in the first footnote. If that is unneeded, please comment it out.
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}
\begin{document}

\title{Vanguard-WSN: A Utility-Driven Energy-Balanced Path Tree Framework for Maximizing Wireless Sensor Network Lifetime}

\author{\IEEEauthorblockN{Deepika A}
\IEEEauthorblockA{\textit{Department of Mathematics} \\
\textit{Amrita School of Physical Sciences}\\
Coimbatore, Amrita Vishwa Vidyapeetham, India \\
cb.ps.i5das23026@cb.students.amrita.edu}
\and
\IEEEauthorblockN{Aishvarya G}
\IEEEauthorblockA{\textit{Department of Mathematics} \\
\textit{Amrita School of Physical Sciences}\\
Coimbatore, Amrita Vishwa Vidyapeetham, India \\
cb.ps.i5das23046@cb.students.amrita.edu}
\and
\IEEEauthorblockN{Gayatri K}
\IEEEauthorblockA{\textit{Department of Mathematics} \\
\textit{Amrita School of Physical Sciences}\\
Coimbatore, Amrita Vishwa Vidyapeetham, India \\
cb.ps.i5das23049@cb.students.amrita.edu}
\and
\IEEEauthorblockN{Anjana A}
\IEEEauthorblockA{\textit{Department of Mathematics} \\
\textit{Amrita School of Physical Sciences}\\
Coimbatore, Amrita Vishwa Vidyapeetham, India \\
cb.ps.i5das23055@cb.students.amrita.edu}
}

\maketitle

\begin{abstract}
In modern Internet of Things (IoT) systems Wireless Sensor Networks (WSNs) holds an irreplaceable position, but their lifetime is often limited by the problem of Energy Hole. Here nodes near the Base Station drain their energy quickly because they handle most of the data forwarding, which can cause the network to break apart. Old routing protocols  such as LEACH, HEED, and PEGASIS try to reduce this issue using random rotation or chain-based structures. However, that methods achieve only about 10–15\% of the network’s theoretical maximum lifetime. Vanguard-WSN, a new framework that replaces random decision-making with a utility-based deterministic approach. The framework includes two key innovations: (1) a Composite Utility Index (Ui) that selects Cluster Heads based on remaining energy and network position, and (2) an Energy-Balanced Path Tree (EBPT) that uses an adaptive load-balancing factor ($\gamma$) to adjust multi-hop routes and prevent energy hotspots. After testing the system through over 30 simulations on a 100-node network, it was found that Vanguard-WSN is better than older systems. The First Node Death (FND) occurs at Round 993.1, which is over ten times longer than LEACH (FND = 97.3). When compared with a Theoretical God-Line (LP-Bound), Vanguard achieves 92\% of the optimal lifetime (R2=0.94). The system achieves a Packet Success Ratio of 98.4\% and delivers 955\% more data packets than LEACH. A formal analysis shows that the algorithm runs in O(NlogN) time, meaning it remains efficient even as the network size increases, making it practical for low-power microcontrollers. These results show that Vanguard-WSN provides a highly efficient and practical solution for mission-critical WSN applications.
\end{abstract}

\begin{IEEEkeywords}
Energy-Balanced Path Tree, Energy Efficiency, Network Lifetime Optimization, IoT, Wireless Sensor Networks, Cluster Head Selection
\end{IEEEkeywords}
"""

    # Manually constructed body to ensure correct LaTeX formatting
    latex_body = r"""
\section{Introduction}

\subsection{The Evolution of Wireless Ad-hoc Networking}
Over the last two decades, wireless networks have changed a lot from concentrated and complex models to flexible, independent networking environments by the idea of Mobile Ad-hoc Network. A Mobile Ad Hoc Network (MANET) is an autonomous network made up of devices that connect to each other wirelessly without any fixed network setup. What makes a MANET unique is its constantly changing nature. Each device is not just sending or receiving data; it also helps forward data for other devices, keeping the whole network connected. Because there is no need for any fixed network setup, MANETs can be quickly set up in emergencies or temporary situations.

However, this flexibility also creates challenges. Managing resources in a MANET is difficult. Unlike wired networks, where power supply and bandwidth are stable, MANET devices run on limited battery power and depends on wireless links that are not always stable. As the need for continuous and widespread connectivity increases, researchers have focused more on a specific type of ad hoc network called the Wireless Sensor Network (WSN), which is designed for sensing and monitoring tasks under similar constraints.

\begin{figure}[htbp]
\centerline{\fbox{Figure 1 placeholder}}
\caption{Vanguard-WSN Architecture}
\label{fig1}
\end{figure}

\subsection{Transition to Wireless Sensor Networks (WSNs)}
Wireless Sensor Networks (WSNs) is an advanced form of MANET technology. While MANET nodes are associated with devices which are carried by humans such as smartphones, laptops, radio sets, etc., WSN nodes are associated with hundreds or thousands of tiny, low-power devices placed in the environment. These nodes can do sensing, process data, and communicate with each other. They are used to observe substantial or ecological circumstances such as pressure, temperature, motion, or sound.

\subsubsection{Critical Applications}
WSNs is very useful in many important areas in this modern society like:
\begin{itemize}
    \item Precision Agriculture: Monitoring soil moisture and nutrient levels to optimize irrigation.
    \item Structural Health Monitoring (SHM): finding cracks or vibrations in bridges and skyscrapers.
    \item Battlefield Surveillance: Detecting enemy movement in restricted areas.
    \item Industrial IoT (IIoT): Predicting maintenance of factory machinery.
\end{itemize}
In all these scenarios, the most important factor is the "lifetime" or how long the network can work. Network’s lifetime means the time until an area of the network is no longer properly monitored because a sensor stops working, or the first “coverage gap” appears is the most critical performance metric. Since batteries are non-replaceable, the death of a node is permanent.

\begin{figure}[htbp]
\centerline{\fbox{Figure 2 placeholder}}
\caption{Initial Network Deployment}
\label{fig2}
\end{figure}

Protocols like LEACH try to solve this problem by randomly rotating leadership roles. However, they often do not consider how nodes are physically distributed in the network. Therefore, low remaining energy nodes may be set as leader nodes, which can speed up the failure of the network.

\subsection{The Vanguard-WSN Approach}
This work introduces Vanguard-WSN, a framework that combines self- managing networking with mathematically optimal energy control. The core idea of our work is the Energy-Balanced Path Tree (EBPT). Unlike minimum-hop routing, EBPT adjusts paths based on an adaptive cost function, routing around energy-depleted nodes to prevent hotspot formation.
Here the system utilizes Utility-Based Cluster Head Selection mechanism nodes based on residual energy (energy remaining in nodes) and local density (how well leader nodes connected to nearby nodes). In this way capable nodes bridge gap between heuristic ad-hoc routing and optimal control theory.

\subsection{Magnitude of the Research}
The research significance is in benchmarking it formed against Theoretical God-Line (LP-Bound). Simulation results, which are detailed in Section 5, demonstrate that Vanguard-WSN extends network stability (FND) by over 1,000\% (10.21x) compared to other existing methods. This leap is achieved through smart network structure rather than expensive and complicated hardware, setting up a new standard for sustainable IoT deployments.

\subsection{Body of the Paper}
The remaining content arranged like: Section 2 contains primary contributions of Vanguard framework. Section 3 provides review of related work, also analyzing the limitations of protocols like LEACH and HEED. Section 4 explains the proposed method, also how the Utility Index (Ui) and the EBPT algorithm are developed. Section 5 includes Simulation Results and Numerical Analysis, which deeply dive into analysis of performance. Finally, Section 6 contains a conclusion.

\section{Main Contribution: The Vanguard Framework}

\subsection{Bridging the God-Line Gap}
The main motive for developing Vanguard-WSN is the large gap between how existing routing protocols perform in practice and the maximum possible lifetime of Wireless Sensor Network (WSN). Throughout the research, this theoretical maximum is called the "God-Line". It represents the longest possible network lifetime that could be achieved if a controller had complete knowledge of every packet transmission and could perfectly distribute the energy load among all nodes.

\subsubsection{Defining the Performance Gap}
The initial analysis showed that older protocols like LEACH and HEED often perform at only 10-15\% of the network’s theoretical maximum. This large "performance gap" is because they make decisions based only on the local information. These protocols optimize for the next round (greedy approach) or the nearest neighbors, whereas the God-Line assumes a complete, long-term optimization across the entire network. Vanguard-WSN is designed to close this gap by better energy balancing across all nodes, and it helps the network last much longer.

\subsection{Energy-Balanced Path Tree (EBPT) Architecture}

\begin{figure}[htbp]
\centerline{\fbox{Figure 3 placeholder}}
\caption{EBPT Routing Tree}
\label{fig3}
\end{figure}

Unlike fixed routing methods that always choose the shortest path and end up quickly using up the energy of the same nodes near the base station, EBPT takes a smarter approach. It prefers nodes that still have plenty of energy and are not handling too much traffic. As these relay nodes begin to lose power, the routing paths automatically change and shift traffic to nodes with more remaining energy. This helps prevent repeated heavy use of nodes near the base station.

\subsection{Comprehensive System Model}
To make our simulation results easy to reproduce and clearly understandable, we describe the network, radio, and traffic models used in this study.

\subsubsection{Network Topology Assumptions}
Assuming a network of N sensor nodes (usually N = 100) that are randomly placed in a square sensing area of size M$\times$M. The Base Station (BS) is located at the center of this area.
The following assumptions are used:
\begin{itemize}
    \item Stationary Nodes: After deployment, both the sensor nodes and the Base Station remain in fixed positions.
    \item Identical Nodes: All sensor nodes start with the same initial energy level $E_0$.
    \item Location Awareness: Each node knows its own position and the position of the Base Station, using GPS or signal-based methods.
    \item Symmetric Communication: The energy needed to send data between two nodes is the same in both directions.
\end{itemize}

\subsubsection{Radio Energy Dissipation Model}
Vanguard-WSN follows the commonly used First-Order Radio Energy Model to estimate communication energy costs. The energy required to transmit a $k$-bit packet over distance $d$ is given by:

\begin{equation}
E_{Tx}(k, d) = \begin{cases} 
k \cdot E_{elec} + k \cdot \epsilon_{fs} \cdot d^2 & \text{if } d < d_0 \\
k \cdot E_{elec} + k \cdot \epsilon_{mp} \cdot d^4 & \text{if } d \ge d_0 
\end{cases}
\end{equation}

Where:
\begin{itemize}
    \item $E_{elec}$: Energy dissipated per bit to operate transmitter/receiver circuitry (typically 50 nJ/bit)
    \item $\epsilon_{fs}$: Free-space amplifier energy (10 pJ/bit/$m^2$)
    \item $\epsilon_{mp}$: Multipath fading amplifier energy (0.0013 pJ/bit/$m^4$)
    \item $d_0$: Crossover transmission distance 
\end{itemize}

Substituting standard values:
\begin{equation}
d_0 = \sqrt{\frac{\epsilon_{fs}}{\epsilon_{mp}}}
\end{equation}
($d_0 \approx 87$ m when rounded)

Energy for Reception:
To receive a $k$-bit packet:
\begin{equation}
E_{Rx}(k) = k \cdot E_{elec}
\end{equation}

This two-part energy cost is important ($d^2$ vs $d^4$). Vanguard's EBPT avoids long-range transmissions that cross the $d_0$ threshold unless necessary, prioritizing multi-hop paths composed of short, low energy links.

\subsubsection{Data Aggregation Model}
Hierarchical routing becomes inefficient if data is not combined before forwarding. In Vanguard, Cluster Heads (CHs) perform data fusion. When a CH receives packets from its child nodes, it combines them into one single packet of fixed size $k$.
The energy used for this process depends on $E_{DA}$, which represents the energy required per bit for data aggregation (5 nJ/bit). This linear model shows the energy cost of basic operations such as averaging or compressing sensor readings (example, temperature data) before sending them to the Base Station.

\subsection{Multi-Dimensional Performance Analysis}
The advantages of the Vanguard framework are not limited to just one measure. Although network lifetime (measured by First Node Death, FND) is the main focus, it is also important that the network remains fair and reliable during operation.

We compare Vanguard’s performance with LEACH and the theoretical upper bound (God-Line):
\begin{itemize}
    \item Lifetime: More than a tenfold increase in network stability, with a 10.21$\times$ improvement in FND.
    \item Fairness: Energy use is evenly distributed across nodes through the adaptive load-balancing factor $\gamma$ (gamma)
    \item Reliability: A high packet delivery rate is maintained using self-adjusting tree structures.
    \item Efficiency: Energy consumption per bit is reduced by avoiding costly long-distance transmissions.
\end{itemize}
Overall, Vanguard-WSN brings real-world performance much closer to the theoretical maximum. These results show that understanding and using network structure across layers is essential for building long-lasting wireless sensor networks.

\section{Background and Related Work}

\subsection{Overview of Clustering in Wireless Sensor Networks}
Clustering in Wireless Sensor Networks (WSNs) was introduced to deal with the limited battery power of sensor nodes. In a flat network, every node sends its data directly to the Base Station (BS). Because transmission energy increases rapidly with distance either with the square of the distance or even the fourth power ($d^4$) nodes that are farther from the BS lose energy much faster than those closer to it. This uneven energy drain can quickly break the network into disconnected parts.

Clustering organizes the network into smaller groups, each controlled by a Cluster Head (CH). The CH collects data from nearby nodes, combines it, and then forwards it to the BS. This reduces the total number of transmissions and allows most nodes to send data over short, energy-efficient distances. However, the success of this approach depends heavily on how well the CHs are chosen. Many traditional protocols select CHs randomly or probabilistically. While this keeps the design simple, it often leads to unstable behaviour and fails to prevent uneven energy use, commonly referred to as the Energy Hole Problem.

\subsection{Detailed Analysis of Legacy Protocols}

\subsubsection{LEACH: The Probabilistic Pioneer}
Low-Energy Adaptive Clustering Hierarchy (LEACH), proposed by Heinzelman et al. [1], was the first major protocol to introduce the idea of rotating cluster heads in Wireless Sensor Networks. The main goal of LEACH is simple: instead of letting a few nodes drain their energy by acting as cluster heads all the time, the responsibility is shared among all nodes over multiple rounds.

To achieve this, LEACH uses a probabilistic threshold function T(n) to decide which nodes become cluster heads in each round:
\begin{equation}
T(n) = \frac{p}{1 - p(r \mod \frac{1}{p})} \quad \forall n \in G
\end{equation}

Here, $p$ represents the desired fraction of cluster heads (usually around 5\%), $r$ is the current round number, and $G$ is the set of nodes that have not acted as cluster heads in the last $1/p$ rounds.

Key Limitation:
Although LEACH succeeds in rotating the cluster head role, it does so without considering the actual condition of the nodes. The selection process is completely random and does not account for residual energy. As a result, a node with very low remaining energy can be chosen as a cluster head just as easily as a fully charged node, as long as it has not recently held the role.
In addition, LEACH assumes that every cluster head can directly communicate with the base station using a single-hop transmission. This assumption works only for small network areas. In larger deployments (greater than 100 meters), cluster heads located far from the base station consume excessive energy while transmitting data, causing them to die quickly. This leads to what is commonly referred to as an edge collapse, where nodes near the network boundary fail much earlier than others.

\subsubsection{HEED: Iterative Energy Awareness}
The Hybrid Energy-Efficient Distributed (HEED) clustering protocol [2] was proposed as a direct response to one of LEACH’s biggest weaknesses: its inability to consider how much energy a node has left. Instead of treating all nodes equally, HEED attempts to make smarter choices by giving preference to nodes with higher remaining energy when selecting cluster heads.

HEED follows a two-stage process.
In the initialization stage, each node computes its likelihood of becoming a cluster head using
\begin{equation}
CH_{prob} = C_{prob} \times \frac{E_{residual}}{E_{max}}
\end{equation}
This simple adjustment ensures that nodes with more available energy are more likely to take on the demanding role of a cluster head.

Next comes the iterative selection stage. Nodes repeatedly exchange tentative cluster-head messages with their neighbours. If a node detects a nearby cluster head that offers a lower communication cost or better energy profile, it joins that cluster. Otherwise, it increases its own probability of becoming a cluster head and tries again. This process continues until every node settles into a cluster.

Where HEED Falls Short:
Although HEED makes better-informed cluster-head decisions than LEACH, it introduces a new problem: excessive overhead. The repeated message exchanges required during the selection phase generate many control packets before any useful data is even transmitted. For energy-limited sensor networks, this organizational cost is far from trivial, it drains batteries simply to establish the network structure.

By contrast, Vanguard-WSN avoids this inefficiency entirely. Cluster-head selection is completed in a single, deterministic step, eliminating iterative negotiations and unnecessary control traffic. As a result, Vanguard-WSN preserves energy for actual sensing and data transmission, rather than wasting it on network setup.

\subsubsection{PEGASIS: The Chain-Based Extremity}
Power-Efficient Gathering in Sensor Information Systems (PEGASIS) [3] takes a chain-based approach instead of clustering. Each node communicates only with its nearest neighbour, aggregates data, and forwards it along the chain until a designated leader transmits the final packet to the Base Station.

While this minimizes per-hop transmission energy, it introduces two major limitations. First, latency grows linearly with network size—data from one end of a 100-node chain must pass through 99 hops before reaching the sink. Second, the chain is fragile: the failure of a single node breaks the entire structure, forcing costly global reconstruction.

Vanguard-WSN avoids these issues by using a tree-based topology, preserving short-hop energy efficiency while enabling parallel data flow, lower delay  and greater resilience to node failures.

\subsection{Modern Approaches: AI and Swarm Intelligence}
Recent research has shifted toward centralized AI-based optimization methods, using techniques such as Genetic Algorithms (GA) [4], Particle Swarm Optimization (PSO) [5], and Reinforcement Learning (RL) [6] to select optimal CH sets.

\begin{itemize}
    \item Swarm Intelligence: Protocols like PSO-C define a performance score for the overall network and gradually improve a group of possible solutions over time. While these methods are theoretically optimal, they require the Base Station to know the exact energy level of every node and to perform complex and time-consuming calculations in each round.
    \item Reinforcement Learning: Reinforcement Learning based routing agents learn through trial and error. However, these methods take long time to provide a good solution, and this training period can take longer than the battery life of the sensor nodes.
\end{itemize}

The Vanguard Advantage: Vanguard-WSN avoids the Difficulty of AI in favor of Deterministic Utility. By defining an algebraic utility function $U_i$ that aligns with 94\% with the best LP-bound (God-Line), we achieve "AI-level" performance with simple arithmetic operation $O(1)$.

\subsection{Qualitative Comparison and Taxonomy}
The table below places Vanguard-WSN within the fits within the classification of routing protocols in wireless sensor networks (WSNs).

\begin{figure}[htbp]
\centerline{\fbox{Table Placeholder - Qualitative Comparison}}
\caption{Qualitative Comparison}
\label{tab_qual}
\end{figure}

Vanguard-WSN combines the best ideas from earlier routing techniques. It is simple, saves energy, and forwards data efficiently, while reducing the weaknesses seen in previous approaches through the EBPT design.

\section{Methodology: Utility-Driven Path Selection}

\subsection{Introduction to Deterministic Utility}
The main change introduced in Vanguard-WSN is the shift from random role rotation to a utility based deterministic approach. Instead of choosing leaders randomly, the system selects them based on clear and measurable information. In environments where energy and resources are limited, choosing nodes randomly can waste energy. So, the system selects cluster heads (CH) and decides routes based on the actual condition of each node, such as how much energy it has left, how well it is connected in the network, and how much traffic it is handling. This section explains how the Utility Index ($U_i$) is mathematically derived and how the Energy-Balanced Path Tree (EBPT) is constructed.

\subsection{The Utility Index $U_i$ Formulation}
To measure how suitable a node $i$ is to act as a main relay node, we define a combined score called $U_i$. This score brings together different physical factors into one single value, which the SDN controller then uses to make decisions.

Utility Function:
\begin{equation}
U_i = \alpha \cdot \frac{E_{res}(i)}{E_{max}} + \beta \cdot \frac{1}{1 + Deg(i)}
\end{equation}

where:
\begin{itemize}
    \item $E_{res}(i)$: Residual energy of node $i$
    \item $Deg(i)$: Neighbor degree (number of peers within range)
    \item $\alpha, \beta$: Weighting coefficients such that $\alpha + \beta = 1$
\end{itemize}

\subsubsection{Component Intuition}
\begin{enumerate}
    \item Energy Weight $\alpha$: Remaining energy of basic sensing tasks are saved as in the later stages of the network's lifetime, cluster heads (CH) with low battery are made sure to be not selected by increasing the value of $\alpha$.
    \item Density Weight $\beta$: This term reduces the chances of selecting nodes from high-density areas. Standard heuristics often select CHs in dense regions to maximize connectivity. However, this leads to quick energy loss of those regions (Hotspots). By giving lower priority to high degrees, Vanguard encourages the selection of CHs in sparser regions, spreading the load to the edges of the network.
\end{enumerate}

\subsection{Algorithm 1: Utility-Based CH Selection}
The CH selection process is executed centrally at the Base Station (or logically centralized SDN controller) to ensure global optimality.

\begin{figure}[htbp]
\centering
\fbox{
\begin{minipage}{0.9\columnwidth}
\textbf{Algorithm 1: Utility-Based CH Selection} \\
\textbf{Input:} set of nodes $N$, threshold $\tau$ \\
\textbf{Output:} set of Cluster Heads $CH_{set}$

1. FOR each node $i$ in $N$: \\
2. \quad Receive heartbeat($ID_i, E_{res\_i}, Location_i$) \\
3. \quad Calculate Degree deg($i$) based on neighbor table \\
4. \quad Compute $U_i = \alpha * (E_{res\_i} / E_{max}) + \beta * (1 / (1 + deg(i)))$ \\
5. END FOR \\
6. Calculate dynamic threshold $\tau = Mean(U)$ \\
7. $CH_{set} = \{\}$ \\
8. FOR each node $i$ in $N$: \\
9. \quad IF $U_i > \tau$ AND TimeSinceLastCH($i$) $> \Gamma_{Holdoff}$: \\
10. \qquad $CH_{set}$.add($i$) \\
11. \qquad Broadcast CH\_Advertisement($i$) \\
12. \quad ELSE: \\
13. \qquad Node $i$ enters 'Member' state \\
14. END IF \\
15. RETURN $CH_{set}$
\end{minipage}
}
\end{figure}

Measurement of the "TimeSinceLastCH" timer ensures that even high-value nodes are given a rest period, preventing thermal runaway or battery fatigue.

\subsection{Energy-Balanced Path Tree (EBPT) Construction}
Once CHs are selected, the network must form a multi-hop path to send data to the sink. The EBPT is a Directed Acyclic Graph (DAG) rooted at the Base Station.

\subsubsection{Submodular Optimization Logic}
The construction of the EBPT can be viewed as a greedy approximation of a submodular optimization problem. We try to maximize the "Network Lifetime" function.
\begin{enumerate}
    \item Distance Sorting: Nodes are arranged based on their Euclidean distance from the Base Station. This ensures that the tree is built starting from the Base Station and expanding outward, which prevents the loop formation.
    \item Parent Selection: For each node $u$, we examine a set of possible parent nodes $P_u$, which are nodes located closer to the Base Station. The best parent $v$ is selected to maximize:
\end{enumerate}

Edge Weight Function
\begin{equation}
W(u, v) = \frac{E_{res}(v)^\gamma}{Cost(u, v) \times (1 + Load(v))}
\end{equation}

Where $Load(v)$ is the Recursive sum of all children currently attached to node $v$.

\subsubsection{Adaptive $\gamma$ Factor}
The $\gamma$ (Gamma) factor is the "tuning knob" of the Vanguard framework.
\begin{itemize}
    \item Low $\gamma$: The network behaves like a shortest-path tree, prioritizing energy efficiency (minimized hops).
    \item High $\gamma$: The network gives less priority to heavy nodes, making data travel through longer routes to prevent energy hotspots.
\end{itemize}

Our Adaptive Gamma Tuner monitors the variance of energy across the network. As $\sigma^2$ increases (indicating energy imbalance), $\gamma$ is automatically incremented. This forces the tree to "widen," using edge nodes and naturally healing energy holes.

\subsection{Complexity Analysis}
To make sure Vanguard-WSN works on low-power hardware, we analyze the computational complexity.

\subsubsection{Time Complexity}
\begin{itemize}
    \item CH Selection: Calculating $U_i$ for all nodes is a linear operation, O(N).
    \item Sorting: Sorting nodes by distance requires $O(N \log N)$.
    \item Tree Construction: Each node checks k neighbours. In the worst case $k=N$, which leads to $O(N^2)$. However, with a fixed transmission radius, k is constant or small, making this O(N).
    \item Total Complexity: The dominant term is the sort, making the overall complexity $O(N \log N)$. This is more efficient than iterative approaches like HEED ($O(N \times Iterations)$) or Swarm Intelligence based Approaches ($O(N^2)$ or higher).
\end{itemize}

\subsubsection{Message Complexity}
Vanguard use an important mechanism where each node sends 1 packet to the BS per round. The BS replies with a single broadcast schedule. Thus, message complexity is O(N), the theoretical minimum for any centralized protocol.

\subsection{Theoretical Convergence}
The EBPT structure is guaranteed to create a connected graph if the nodes are placed densely enough to meet the minimum connectivity requirement. Since the parent selection metric $W(u, v)$ is strictly positive and the distance sorting prevents back propagation, The algorithm is loop-free and builds a proper tree structure in a fixed number of steps. This determinism is crucial for "hard real-time" monitoring applications.

\section{Simulation and Numerical Analysis}

\subsection{Experimental Setup}
To carefully test the proposed framework. We ran several simulations to compare Vanguard-WSN against LEACH, HEED, and PEGASIS baselines. The simulation setup was created using a custom discrete-event simulator written in Python, following the First-Order Radio Model parameters commonly used in wireless sensor network research.

\subsubsection{Simulation Parameters}
The specific configuration used for all reported experiments is detailed below.

\begin{table}[htbp]
\caption{Simulation Settings and Parameters}
\begin{center}
\begin{tabular}{|c|c|}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
Network Size & 100 Nodes \\
Area & 100m x 100m \\
BS Location & (50, 50) \\
Initial Energy & 0.5 J \\
Data Packet Size & 4000 bits \\
Control Packet Size & 200 bits \\
\hline
\end{tabular}
\label{tab1}
\end{center}
\end{table}

\subsection{Network Stability Analysis (FND)}

\begin{figure}[htbp]
\centerline{\fbox{Figure 4 placeholder}}
\caption{Network Stability (FND)}
\label{fig4}
\end{figure}

The above figure compares the network lifetime by the number of alive nodes of different protocol. The First Node Death (FND) is used to measure when the first node runs out of energy during the simulation for a 50-node network. LEACH experiences its FND at approximately Round 97, roughly 5\% of rounds. The early failure is due to probabilistic selection of Cluster Heads, where nodes with low residual energy may still be assigned energy- intensive communication roles. HEED performs marginally better (FND $\approx$ 210). However, the performance is limited by additional control overhead and repeated cluster formation procedures.
In contrast, the proposed Vanguard-WSN protocol maintains all nodes alive until Round 993.1. The proposed method significantly delays the first node death compared to LEACH and HEED. By dynamically adjusting the relay burden away from weakest nodes, the proposed method distributes the energy consumption more uniformly across the network. Hence, no single node fails and network remains fully functional for a significantly longer duration compared to other protocols.

\subsection{Comparative Death Curves}

\begin{figure}[htbp]
\centerline{\fbox{Figure 5 placeholder}}
\caption{Comparative Death Curves}
\label{fig5}
\end{figure}

\subsection{Epoch-by-Epoch Network Behaviour}
To examine the operational behaviour of the proposed Vanguard-WSN protocol, the evolution of the network is analysed across three representative time intervals based on the observed changes in routing and energy distribution.
\begin{enumerate}
    \item Early Phase (Round 0-300): The network follows shortest path algorithm for operation. The adaptive $\gamma$ factor remains low because energy variance is minimal. Under this condition, routing decisions primarily favour paths with shorter geometric distance to the sink, resulting in near–shortest-path forwarding behaviour.
    \item Mid life Phase (Round 300-800): Energy variance increases as nodes near sink frequently forward the packets. In response, the adaptive GAMMA Tuner increases the value of $\gamma$ and this alters the behaviour of the energy balanced path selection mechanism, causing a portion of the traffic to be redirected through nodes located farther from the sink.
    \item Terminal Phase (Round 800 -1000): In the final stage of the network, most nodes have very low remaining energy. The utility-based selection function is used to frequently rotate forwarding and leadership roles among the nodes with comparatively higher residual energy. This avoids excessive workload on any individual node and enables the network to remain functional.
\end{enumerate}

\subsection{Benchmarking against the theoretical bound}
The performance of Vanguard-WSN was evaluated against a theoretical upper bound on network lifetime, referred as the God-Line. Our empirical FND shows a correlation coefficient of $R^2 = 0.94$ with the LP-Solved bound, operating at 92\% efficiency. These results show that, despite relying only on local information, Vanguard-WSN achieves performance close to the centralized LP solution in the evaluated simulation setting.

\subsection{Energy Fairness and Redistribution}
To examine how evenly energy is consumed across the network, Jain’s Fairness Index (J) is used to measure the symmetry of residual energy among nodes.

\begin{figure}[htbp]
\centerline{\fbox{Figure 6 placeholder}}
\caption{Jain's Fairness Index}
\label{fig6}
\end{figure}

\subsubsection{Fairness–lifetime trade-off}
In conventional routing protocols, a low fairness index generally indicates unbalanced energy usage. However, in the proposed Vanguard-WSN protocol, a certain degree of imbalance is inherent to the multi-hop routing structure. Nodes located closer to the base station forward more data, so they lose energy faster than nodes at the edges of the network.

The EBPT-based routing strategy intentionally allows these relay nodes to carry a higher forwarding load inorder to protect distant and low-energy nodes from early exhaustion. As a result, energy consumption is redistributed in a structured manner rather than uniformly across all nodes.

\subsection{Data Throughput and Reliability}

\begin{figure}[htbp]
\centerline{\fbox{Figure 7 placeholder}}
\caption{Throughput Analysis}
\label{fig7}
\end{figure}

\begin{figure}[htbp]
\centerline{\fbox{Figure 9 placeholder}}
\caption{State Snapshot (FND Epoch)}
\label{fig9}
\end{figure}

\subsection{Heatmap Proof and Structural Integrity}

\begin{figure}[htbp]
\centerline{\fbox{Figure 8 placeholder}}
\caption{Energy Dissipation Heatmap}
\label{fig8}
\end{figure}

\subsection{Comparative Metrics Summary}
Table 2 summarizes our quantitative results. All values are averaged over 30 trials with 95\% confidence intervals.

\begin{table}[htbp]
\caption{Comparative Performance Metrics}
\begin{center}
\begin{tabular}{|c|c|c|c|}
\hline
\textbf{Protocol} & \textbf{FND (Round)} & \textbf{Throughput} & \textbf{Efficiency} \\
\hline
LEACH & 97.3 & 1x & Low \\
HEED & 210 & 2.1x & Medium \\
PEGASIS & 350 & 1.5x & High (Latency) \\
\textbf{Vanguard} & \textbf{993.1} & \textbf{10.2x} & \textbf{Very High} \\
\hline
\end{tabular}
\label{tab2}
\end{center}
\end{table}

\subsection{Study limitations}
\begin{itemize}
    \item Ideal MAC layer: The simulations assume a collision-free TDMA-based MAC layer, which is commonly adopted for routing protocol evaluation. However, communication delay and underestimate effects in high-interference environments is ignored.
    \item Static sink: A fixed sink is considered in this study. The use of mobile sinks is not explored which may further improve energy balancing.
    \item Radio energy model: The simulation uses a basic first-order radio energy model, and it does not consider effects such as fading or signal reflections.
\end{itemize}

\section{Conclusion}
This paper introduced Vanguard-WSN, a routing framework developed to address the long-standing Energy Hole Problem in Wireless Sensor Networks (WSNs). Unlike conventional protocols that depends on random selection or local optimization, Vanguard-WSN uses a deterministic, utility-based approach to manage the network.

The key innovation introduced in this study is the Energy-Balanced Path Tree (EBPT), which separates sensing from data forwarding to use energy more efficiently. By assigning multi-hop communication tasks only to nodes that are most capable based on energy and network conditions the framework ensures more balanced energy consumption across the network. Simulation results demonstrate a 10.21$\times$ improvement in network stability, measured using First Node Death (FND), compared to the widely adopted LEACH protocol.

Moreover, the strong correlation (94\%) with the theoretical upper-bound lifetime (God-Line benchmark) indicates that distributed methods can achieve results close to the global optimality without depending on computationally intensive linear programming technique. The algorithm maintains practical computational complexity, making it suitable for deployment on resource-constrained hardware.

Overall, the findings suggest that Vanguard-WSN provides a robust and sustainable routing solution for mission-critical WSN applications where network lifetime and reliability are essential.

\begin{thebibliography}{00}
\bibitem{b1} Heinzelman, W. R., Chandrakasan, A., \& Balakrishnan, H. (2000, January). Energy-efficient communication protocol for wireless microsensor networks. In Proceedings of the 33rd annual Hawaii international conference on system sciences (pp. 10-pp). IEEE.
\bibitem{b2} Younis, O., \& Fahmy, S. (2004). HEED: a hybrid, energy-efficient, distributed clustering approach for ad hoc sensor networks. IEEE Transactions on mobile computing, 3(4), 366-379.
\bibitem{b3} Lindsey, S., \& Raghavendra, C. S. (2002, March). PEGASIS: Power-efficient gathering in sensor information systems. In Proceedings, IEEE aerospace conference (Vol. 3, pp. 3-3). IEEE.
\bibitem{b4} Hussain, S., \& Islam, O. (2007, March). An energy efficient spanning tree based multi-hop routing in wireless sensor networks. In 2007 IEEE Wireless Communications and Networking Conference (pp. 4383-4388). IEEE.
\bibitem{b5} Latiff, N. A., Tsimenidis, C. C., \& Sharif, B. S. (2007, September). Energy-aware clustering for wireless sensor networks using particle swarm optimization. In 2007 IEEE 18th international symposium on personal, indoor and mobile radio communications (pp. 1-5). IEEE.
\bibitem{b6} Arroyo-Valles, R., Alaiz-Rodriguez, R., Guerrero-Curieses, A., \& Cid-Sueiro, J. (2007, December). Q-probabilistic routing in wireless sensor networks. In 2007 3rd international conference on intelligent sensors, sensor networks and information (pp. 1-6). IEEE.
\bibitem{b7} Heinzelman, W. B., Chandrakasan, A. P., \& Balakrishnan, H. (2002). An application-specific protocol architecture for wireless microsensor networks. IEEE Transactions on wireless communications, 1(4), 660-670.
\bibitem{b8} Manjeshwar, A., \& Agrawal, D. P. (2001, April). TEEN: ARouting Protocol for Enhanced Efficiency in Wireless Sensor Networks. In ipdps (Vol. 1, No. 2001, p. 189).
\bibitem{b9} Akyildiz, I. F., Su, W., Sankarasubramaniam, Y., \& Cayirci, E. (2002). Wireless sensor networks: a survey. Computer networks, 38(4), 393-422.
\bibitem{b10} Al-Karaki, J. N., \& Kamal, A. E. (2004). Routing techniques in wireless sensor networks: a survey. IEEE wireless communications, 11(6), 6-28.
\bibitem{b11} Abbasi, A. A., \& Younis, M. (2007). A survey on clustering algorithms for wireless sensor networks. Computer communications, 30(14-15), 2826-2841.
\bibitem{b12} Jain, R. K., Chiu, D. M. W., \& Hawe, W. R. (1984). A quantitative measure of fairness and discrimination. Eastern Research Laboratory, Digital Equipment Corporation, Hudson, MA, 21(1), 2022-2023.
\bibitem{b13} Kumar, D., Aseri, T. C., \& Patel, R. (2009). EEHC: Energy efficient heterogeneous clustered scheme for wireless sensor networks. computer communications, 32(4), 662-667.
\bibitem{b14} Singh, S. K., Kumar, P., \& Singh, J. P. (2017). A survey on successors of LEACH protocol. Ieee Access, 5, 4298-4328.
\bibitem{b15} Behera, T. M., Mohapatra, S. K., Samal, U. C., Khan, M. S., Daneshmand, M., \& Gandomi, A. H. (2019). Residual energy-based cluster-head selection in WSNs for IoT application. IEEE Internet of Things Journal, 6(3), 5132-5139.
\bibitem{b16} Hasan, M. Z., Al-Rizzo, H., \& Al-Turjman, F. (2017). A survey on multipath routing protocols for QoS assurances in real-time wireless multimedia sensor networks. IEEE Communications Surveys \& Tutorials, 19(3), 1424-1456.
\bibitem{b17} Rao, P. S., Jana, P. K., \& Banka, H. (2017). A particle swarm optimization based energy efficient cluster head selection algorithm for wireless sensor networks. Wireless networks, 23(7), 2005-2020.
\bibitem{b18} Darabkh, K. A., Al-Maaitah, N. J., Jafar, I. F., \& Khalifeh, A. F. (2018). EA-CRP: a novel energy-aware clustering and routing protocol in wireless sensor networks. Computers \& Electrical Engineering, 72, 702-718.
\bibitem{b19} Sara, G. S., \& Sridharan, D. (2014). Routing in mobile wireless sensor network: A survey. Telecommunication Systems, 57(1), 51-79.
\end{thebibliography}

\vspace{12pt}

\end{document}
"""
    with open('Vanguard_IEEE_Formatted.tex', 'w', encoding='utf-8') as f:
        f.write(latex_header)
        f.write(latex_body)
    print("Vanguard_IEEE_Formatted.tex created successfully.")

if __name__ == "__main__":
    create_latex_doc()
