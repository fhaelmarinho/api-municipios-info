HTML_INTERFACE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Consulta de Municípios do Brasil - IBGE</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col">
  <!-- Top Navigation -->
  <header class="bg-indigo-700 text-white shadow-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <span class="text-2xl">📍</span>
        <div>
          <h1 class="font-bold text-lg leading-tight">Municípios do Brasil</h1>
          <p class="text-xs text-indigo-200">Dados oficiais via API IBGE</p>
        </div>
      </div>
      <div class="flex items-center space-x-3 text-sm">
        <a href="/docs" class="bg-white/10 hover:bg-white/20 transition px-3 py-1.5 rounded-lg font-medium flex items-center space-x-1 border border-white/20">
          <span>📖</span>
          <span>Swagger UI</span>
        </a>
        <a href="/redoc" class="bg-white/10 hover:bg-white/20 transition px-3 py-1.5 rounded-lg font-medium hidden sm:flex items-center space-x-1 border border-white/20">
          <span>📄</span>
          <span>ReDoc</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
    <!-- Hero / Controls Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8">
      <div class="max-w-3xl">
        <h2 class="text-2xl font-bold text-slate-900 mb-2">Consulta Online sem Terminal</h2>
        <p class="text-slate-600 mb-6 text-sm sm:text-base">
          Selecione uma Unidade Federativa para visualizar os municípios, buscar cidades pelo nome e exportar os relatórios em formato TXT ou planilha CSV.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <!-- Estado Dropdown -->
        <div class="md:col-span-4">
          <label for="select-uf" class="block text-sm font-semibold text-slate-700 mb-1.5">
            Estado (UF)
          </label>
          <select id="select-uf" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-800 font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none transition">
            <option value="" disabled selected>Carregando estados...</option>
          </select>
        </div>

        <!-- Filtro por Nome -->
        <div class="md:col-span-5">
          <label for="input-busca" class="block text-sm font-semibold text-slate-700 mb-1.5">
            Filtrar Município
          </label>
          <div class="relative">
            <input
              type="text"
              id="input-busca"
              placeholder="Digite o nome de uma cidade..."
              class="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-slate-800 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
              disabled
            />
            <span class="absolute left-3.5 top-3 text-slate-400">🔍</span>
          </div>
        </div>

        <!-- Botões de Exportação -->
        <div class="md:col-span-3 flex space-x-2">
          <a
            id="btn-txt"
            href="#"
            target="_blank"
            class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-center py-2.5 px-3 rounded-xl font-medium text-sm transition border border-slate-300 pointer-events-none opacity-50 flex items-center justify-center space-x-1"
          >
            <span>📄</span>
            <span>TXT</span>
          </a>
          <a
            id="btn-csv"
            href="#"
            target="_blank"
            class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-center py-2.5 px-3 rounded-xl font-medium text-sm transition shadow-sm pointer-events-none opacity-50 flex items-center justify-center space-x-1"
          >
            <span>📊</span>
            <span>CSV</span>
          </a>
        </div>
      </div>

      <!-- Live Info Bar -->
      <div id="info-bar" class="mt-6 pt-6 border-t border-slate-100 hidden flex-wrap items-center justify-between gap-4 text-sm">
        <div class="flex items-center space-x-4">
          <span class="text-slate-500">Estado: <strong id="info-estado" class="text-slate-900">-</strong></span>
          <span class="text-slate-500">Região: <strong id="info-regiao" class="text-slate-900">-</strong></span>
          <span class="text-slate-500">Total: <strong id="info-total" class="text-indigo-600 font-bold">0</strong> municípios</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-xs text-slate-400">Origem:</span>
          <span id="badge-origem" class="bg-indigo-50 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-semibold border border-indigo-200">API IBGE</span>
        </div>
      </div>
    </div>

    <!-- Status / Loading Indicator -->
    <div id="loading" class="hidden text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent"></div>
      <p class="mt-3 text-slate-500 text-sm">Consultando dados do IBGE...</p>
    </div>

    <!-- Empty State -->
    <div id="empty-state" class="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
      <span class="text-5xl block mb-3">🗺️</span>
      <h3 class="text-lg font-semibold text-slate-800">Selecione um Estado</h3>
      <p class="text-slate-500 text-sm max-w-sm mx-auto mt-1">
        Escolha uma UF no menu acima para carregar a lista completa de cidades e suas regiões.
      </p>
    </div>

    <!-- Results Table Container -->
    <div id="results-container" class="hidden bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-slate-700">
          <thead class="bg-slate-50 border-b border-slate-200 text-xs uppercase font-semibold text-slate-500">
            <tr>
              <th scope="col" class="px-6 py-3.5 w-16">#</th>
              <th scope="col" class="px-6 py-3.5">Município</th>
              <th scope="col" class="px-6 py-3.5">Microrregião</th>
              <th scope="col" class="px-6 py-3.5">Mesorregião</th>
              <th scope="col" class="px-6 py-3.5 text-right">Código IBGE</th>
            </tr>
          </thead>
          <tbody id="tabela-corpo" class="divide-y divide-slate-100">
            <!-- Dynamic rows inserted via JS -->
          </tbody>
        </table>
      </div>
      <div id="nenhum-resultado" class="hidden text-center py-10 text-slate-500 text-sm">
        Nenhum município encontrado com o termo pesquisado.
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4">
      <p>Dados disponibilizados pelo <strong>IBGE</strong> (Instituto Brasileiro de Geografia e Estatística).</p>
      <p class="mt-1">
        Acesse a documentação interativa em <a href="/docs" class="text-indigo-600 hover:underline">/docs</a> ou <a href="/redoc" class="text-indigo-600 hover:underline">/redoc</a>.
      </p>
    </div>
  </footer>

  <!-- Client Script -->
  <script>
    let todosMunicipios = [];
    const selectUf = document.getElementById('select-uf');
    const inputBusca = document.getElementById('input-busca');
    const btnTxt = document.getElementById('btn-txt');
    const btnCsv = document.getElementById('btn-csv');
    const infoBar = document.getElementById('info-bar');
    const infoEstado = document.getElementById('info-estado');
    const infoRegiao = document.getElementById('info-regiao');
    const infoTotal = document.getElementById('info-total');
    const badgeOrigem = document.getElementById('badge-origem');
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('empty-state');
    const resultsContainer = document.getElementById('results-container');
    const tabelaCorpo = document.getElementById('tabela-corpo');
    const nenhumResultado = document.getElementById('nenhum-resultado');

    // 1. Carregar lista de Estados ao abrir a página
    async function carregarEstados() {
      try {
        const res = await fetch('/api/v1/estados');
        const estados = await res.json();
        selectUf.innerHTML = '<option value="" disabled selected>Selecione um estado...</option>';
        estados.forEach(e => {
          const opt = document.createElement('option');
          opt.value = e.sigla;
          opt.textContent = `${e.nome} (${e.sigla})`;
          selectUf.appendChild(opt);
        });
      } catch (err) {
        selectUf.innerHTML = '<option value="" disabled selected>Erro ao carregar estados</option>';
        console.error(err);
      }
    }

    // 2. Consultar municípios da UF selecionada
    async function consultarMunicipios(uf) {
      loading.classList.remove('hidden');
      emptyState.classList.add('hidden');
      resultsContainer.classList.add('hidden');
      infoBar.classList.add('hidden');
      inputBusca.disabled = true;
      inputBusca.value = '';

      btnTxt.href = `/api/v1/municipios/${uf}/exportar/txt`;
      btnCsv.href = `/api/v1/municipios/${uf}/exportar/csv`;
      btnTxt.classList.remove('pointer-events-none', 'opacity-50');
      btnCsv.classList.remove('pointer-events-none', 'opacity-50');

      try {
        const res = await fetch(`/api/v1/municipios/${uf}`);
        if (!res.ok) throw new Error('Falha ao obter municípios');
        const data = await res.json();

        todosMunicipios = data.municipios;
        infoEstado.textContent = data.estado_nome;
        infoRegiao.textContent = data.regiao;
        infoTotal.textContent = data.total;
        badgeOrigem.textContent = data.origem_dados;

        infoBar.classList.remove('hidden');
        resultsContainer.classList.remove('hidden');
        inputBusca.disabled = false;
        renderizarTabela(todosMunicipios);
      } catch (err) {
        alert('Não foi possível carregar os dados deste estado. Tente novamente.');
        console.error(err);
      } finally {
        loading.classList.add('hidden');
      }
    }

    // 3. Renderizar linhas da tabela
    function renderizarTabela(lista) {
      tabelaCorpo.innerHTML = '';
      if (!lista || lista.length === 0) {
        nenhumResultado.classList.remove('hidden');
        return;
      }
      nenhumResultado.classList.add('hidden');

      const frag = document.createDocumentFragment();
      lista.forEach((m, idx) => {
        const tr = document.createElement('tr');
        tr.className = idx % 2 === 0 ? 'bg-white hover:bg-slate-50 transition' : 'bg-slate-50/50 hover:bg-slate-50 transition';
        tr.innerHTML = `
          <td class="px-6 py-3 font-mono text-xs text-slate-400">${idx + 1}</td>
          <td class="px-6 py-3 font-semibold text-slate-900">${m.nome}</td>
          <td class="px-6 py-3 text-slate-600">${m.microrregiao || 'N/A'}</td>
          <td class="px-6 py-3 text-slate-600">${m.mesorregiao || 'N/A'}</td>
          <td class="px-6 py-3 text-right font-mono text-xs text-slate-400">${m.id || '-'}</td>
        `;
        frag.appendChild(tr);
      });
      tabelaCorpo.appendChild(frag);
    }

    // Eventos
    selectUf.addEventListener('change', (e) => consultarMunicipios(e.target.value));

    inputBusca.addEventListener('input', (e) => {
      const termo = e.target.value.toLowerCase().trim();
      const filtrados = todosMunicipios.filter(m => m.nome.toLowerCase().includes(termo));
      renderizarTabela(filtrados);
    });

    carregarEstados();
  </script>
</body>
</html>
"""
