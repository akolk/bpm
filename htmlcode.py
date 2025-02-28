html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!--<script src="https://unpkg.com/bpmn-js/dist/bpmn-viewer.development.js"></script> -->
        <!-- required modeler styles -->
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/bpmn-js.css">
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/diagram-js.css">
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/bpmn-font/css/bpmn.css">

    <!-- modeler distro -->
    <script src="https://unpkg.com/bpmn-js@18.3.1/dist/bpmn-modeler.development.js"></script>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            width: 100%;
            height: 100%;
        }
        #canvas {
            width: 100%;
            height: 100vh;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <div id="canvas"></div>
    <script>
        var viewer = new BpmnJS({ container: '#canvas' });  
        
        async function exportDiagram() {
            try {
               var result = await viewer.saveXML({ format: true });
               alert('Diagram exported. Check the developer tools!');
               console.log('DIAGRAM', result.xml);
            } catch (err) {
               console.error('could not save BPMN 2.0 diagram', err);
            }
        }
        
        async function renderBPMN(xml) {
            await viewer.importXML(xml) 
        }
        window.renderBPMN = renderBPMN;
    </script>

"""
