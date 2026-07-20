"""csharp_ops — Camada 6.8: C#/.NET Scaffold.

Operações para projetos C# no Godot: scaffold, build, script templates.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def scaffold_csharp_project(
    project_path: str | None = None,
    dotnet_version: str = "net8.0",
    create_solution: bool = True,
) -> dict:
    """Cria/scaffolda um projeto C# Godot a partir de um projeto existente.
    
    Args:
        project_path: Caminho do projeto Godot
        dotnet_version: Versão do .NET ("net8.0" ou "net9.0")
        create_solution: Cria arquivo .sln
    
    Returns:
        dict com status e arquivos criados
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if not proj.exists():
            return {"ok": False, "error": f"Projeto não encontrado: {proj}"}
        
        if proj.is_file():
            proj = proj.parent
        
        # Verifica/atualiza project.godot
        project_file = proj / "project.godot"
        if not project_file.exists():
            return {"ok": False, "error": f"project.godot não encontrado em {proj}"}
        
        content = project_file.read_text(encoding="utf-8")
        
        # Habilita editor C#
        if '[dotnet]' not in content:
            content += '\n[dotnet]\nproject/assembly_name="GameScripts"\n'
        
        project_file.write_text(content, encoding="utf-8")
        
        # Cria .csproj
        csproj_name = f"{proj.name}.csproj"
        csproj_path = proj / csproj_name
        
        csproj_content = f'''<Project Sdk="Godot.NET.Sdk/{dotnet_version}">
  <PropertyGroup>
    <TargetFramework>{dotnet_version}</TargetFramework>
    <EnableDynamicLoading>true</EnableDynamicLoading>
    <RootNamespace>{proj.name.replace(' ', '')}</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Godot.SourceGenerators" Version="4.3.0" />
  </ItemGroup>
</Project>
'''
        csproj_path.write_text(csproj_content, encoding="utf-8")
        
        created = [str(csproj_path)]
        
        # Cria .sln
        if create_solution:
            sln_path = proj / f"{proj.name}.sln"
            sln_content = f'''
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{proj.name}", "{csproj_name}", "{{GUID}}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {{GUID}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {{GUID}}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {{GUID}}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {{GUID}}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
EndGlobal
'''
            import uuid
            guid = str(uuid.uuid4()).upper()
            sln_content = sln_content.replace("{GUID}", f"{{{guid}}}")
            sln_path.write_text(sln_content, encoding="utf-8")
            created.append(str(sln_path))
        
        # Cria diretório de scripts se não existir
        scripts_dir = proj / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Cria um script C# de exemplo
        example_script = scripts_dir / "GameManager.cs"
        example_content = f'''using Godot;
using System;

namespace {proj.name.replace(' ', '')};

public partial class GameManager : Node
{{
    public override void _Ready()
    {{
        GD.Print($"[{proj.name}] GameManager inicializado!");
    }}

    public override void _Process(double delta)
    {{
        // Game loop
    }}
}}
'''
        example_script.write_text(example_content, encoding="utf-8")
        created.append(str(example_script))
        
        return {
            "ok": True,
            "project": str(proj),
            "dotnet_version": dotnet_version,
            "files_created": created,
            "message": (
                f"Projeto C# scaffoldado em {proj}. "
                f"{len(created)} arquivos criados. "
                "Abra no Godot para compilar os scripts C#."
            ),
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao scaffoldar C#: {e}"}


def generate_csharp_script(
    script_path: str,
    class_name: str,
    parent_class: str = "Node",
    namespace: str = "",
    template: str = "basic",
) -> dict:
    """Gera um script C# para Godot a partir de templates.
    
    Args:
        script_path: Caminho onde salvar o script .cs
        class_name: Nome da classe C#
        parent_class: Classe base Godot (Node, Node2D, Node3D, Control, etc.)
        namespace: Namespace C# (usa nome do projeto se vazio)
        template: "basic", "player", "enemy", "pickup", "ui"
    
    Returns:
        dict com status e caminho do script
    """
    try:
        sp = Path(script_path)
        sp.parent.mkdir(parents=True, exist_ok=True)
        
        ns = namespace if namespace else "GameScripts"
        usings = ["Godot", "System"]
        
        templates = {
            "basic": (
                usings,
                f'''public partial class {class_name} : {parent_class}
{{
    public override void _Ready()
    {{
        GD.Print("[{class_name}] Pronto!");
    }}

    public override void _Process(double delta)
    {{
    }}
}}'''
            ),
            "player": (
                usings + ["System.Collections.Generic"],
                f'''public partial class {class_name} : {parent_class}
{{
    [Export] public float Speed {{ get; set; }} = 400f;
    [Export] public float JumpVelocity {{ get; set; }} = -450f;
    
    private Vector2 _velocity;
    private bool _isOnFloor;

    public override void _Ready()
    {{
        GD.Print("[{class_name}] Player inicializado!");
    }}

    public override void _PhysicsProcess(double delta)
    {{
        float dt = (float)delta;
        Vector2 input = Input.GetVector("move_left", "move_right", "move_up", "move_down");
        _velocity = new Vector2(input.X * Speed, _velocity.Y);
        
        if (Input.IsActionJustPressed("jump") && _isOnFloor)
        {{
            _velocity.Y = JumpVelocity;
        }}

        _velocity.Y += 980f * dt; // Gravidade
        Velocity = _velocity;
        MoveAndSlide();
        _isOnFloor = IsOnFloor();
    }}
}}'''
            ),
            "enemy": (
                usings + ["System.Collections.Generic"],
                f'''public partial class {class_name} : {parent_class}
{{
    [Export] public float Speed {{ get; set; }} = 100f;
    [Export] public float PatrolRadius {{ get; set; }} = 200f;
    [Export] public int Health {{ get; set; }} = 3;
    
    private Vector2 _startPosition;
    private int _direction = 1;

    public override void _Ready()
    {{
        _startPosition = Position;
        GD.Print("[{class_name}] Inimigo inicializado!");
    }}

    public override void _PhysicsProcess(double delta)
    {{
        float dt = (float)delta;
        
        // Patrulha simples (vai e volta)
        Position += new Vector2(Speed * _direction * dt, 0);
        
        if (Mathf.Abs(Position.X - _startPosition.X) > PatrolRadius)
        {{
            _direction *= -1;
        }}
    }}

    public void TakeDamage(int amount)
    {{
        Health -= amount;
        GD.Print($"[{class_name}] Dano: {{amount}}. HP restante: {{Health}}");
        
        if (Health <= 0)
        {{
            QueueFree();
            GD.Print($"[{class_name}] Derrotado!");
        }}
    }}
}}'''
            ),
            "pickup": (
                usings,
                f'''public partial class {class_name} : {parent_class}
{{
    [Export] public string ItemType {{ get; set; }} = "coin";
    [Export] public int Value {{ get; set; }} = 1;
    [Export] public float BobSpeed {{ get; set; }} = 2f;
    [Export] public float BobHeight {{ get; set; }} = 5f;
    
    private Vector2 _startPosition;

    public override void _Ready()
    {{
        _startPosition = Position;
        if (GetNode<Area2D>("Area2D") is {{ }} area)
        {{
            area.BodyEntered += OnBodyEntered;
        }}
    }}

    public override void _Process(double delta)
    {{
        // Efeito de flutuação
        Position = _startPosition + new Vector2(0, Mathf.Sin((float)Time.GetTicksMsec() / 1000f * BobSpeed) * BobHeight);
    }}

    private void OnBodyEntered(Node2D body)
    {{
        if (body is {class_name}) return;
        GD.Print($"[{class_name}] Coletado por {{body.Name}}! +{{Value}} {{ItemType}}");
        QueueFree();
    }}
}}'''
            ),
            "ui": (
                usings + ["System.Collections.Generic"],
                f'''public partial class {class_name} : {parent_class}
{{
    [Export] public string Title {{ get; set; }} = "Menu";
    
    private readonly List<Button> _buttons = new();

    public override void _Ready()
    {{
        GD.Print($"[{class_name}] {{Title}} carregado!");
        
        // Conecta botões automaticamente
        foreach (var child in GetChildren())
        {{
            if (child is Button btn)
            {{
                _buttons.Add(btn);
                btn.Pressed += () => OnButtonPressed(btn);
            }}
        }}
    }}

    private void OnButtonPressed(Button button)
    {{
        GD.Print($"[{class_name}] Botão pressionado: {{button.Name}}");
    }}

    public void ShowMenu()
    {{
        Visible = true;
    }}

    public void HideMenu()
    {{
        Visible = false;
    }}
}}'''
            ),
        }
        
        template_data = templates.get(template, templates["basic"])
        usings_list = template_data[0]
        class_code = template_data[1]
        
        using_lines = "\n".join(f"using {u};" for u in usings_list)
        
        code = f'''{using_lines}

namespace {ns};

{class_code}
'''
        
        sp.write_text(code, encoding="utf-8")
        
        return {
            "ok": True,
            "script_path": str(sp),
            "class_name": class_name,
            "parent_class": parent_class,
            "template": template,
            "message": f"Script C# '{class_name}' gerado em {sp} (template: {template})",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao gerar script C#: {e}"}


def build_csharp_project(
    project_path: str | None = None,
    configuration: str = "Debug",
) -> dict:
    """Compila o projeto C# do Godot.
    
    Args:
        project_path: Caminho do projeto
        configuration: "Debug" ou "Release"
    
    Returns:
        dict com status da compilação
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if proj.is_file():
            proj = proj.parent
        
        csproj = list(proj.glob("*.csproj"))
        if not csproj:
            return {"ok": False, "error": "Nenhum .csproj encontrado. Execute scaffold_csharp_project primeiro."}
        
        result = subprocess.run(
            ["dotnet", "build", str(csproj[0]), "-c", configuration],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(proj),
        )
        
        return {
            "ok": result.returncode == 0,
            "configuration": configuration,
            "project": str(proj),
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "message": "Compilação OK" if result.returncode == 0 else f"Compilação falhou (exit {result.returncode})",
        }
    except FileNotFoundError:
        return {"ok": False, "error": "dotnet CLI não encontrado. Instale o .NET SDK 8.0+."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout: compilação excedeu 120s"}
    except Exception as e:
        return {"ok": False, "error": f"Erro ao compilar C#: {e}"}
