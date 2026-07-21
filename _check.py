import sys  
sys.path.insert(0, '.')  
from server import PHASE_TOOLSETS, PHASE_TOOLS_CORE  
for phase in ['IDEIA','DESIGN','PROTOTIPO','CONTEUDO','POLIMENTO','PRONTO_PARA_LANCAR']:  
  p = PHASE_TOOLSETS.get(phase, set())  
