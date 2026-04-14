import os
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from ml.predictor import generate_prediction_data
from matplotlib.figure import Figure

def generate_report_pdf(output_path, report_name, num_months):
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
        
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Sales Forecast Report: {num_months} Months", styles['h1']))
    story.append(Spacer(1, 0.25*inch))

    # Predictor-оос өгөгдөл авах (num_months дамжуулна)
    data = generate_prediction_data(num_months=num_months)
    
    if data.get('error'):
        story.append(Paragraph(f"Error: {data['error']}", styles['BodyText']))
    else:
        # График зурах
        fig = Figure(figsize=(7, 3.5), dpi=300)
        ax = fig.add_subplot(111)
        ax.plot(data['historical_x'][-12:], data['historical_y'][-12:], marker='o', label='Actual')
        ax.plot(data['predicted_x'], data['predicted_y'], marker='o', linestyle='--', label='Forecast')
        ax.legend(); ax.grid(True)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.25*inch))

        # Хүснэгт
        table_data = [['Period Index', 'Type', 'Value']]
        for i in range(len(data['predicted_x'])):
            table_data.append([int(data['predicted_x'][i]), "Forecast", f"{data['predicted_y'][i]:,.2f}"])
        
        t = Table(table_data)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(t)

    doc.build(story)