def main():
    app = QApplication(sys.argv)
    mainWindow = SimpleApp()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()